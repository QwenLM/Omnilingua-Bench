"""校验统一 JSONL 的结构、模态引用与时间范围；不执行模型推理或评分。"""

import argparse
import json
import math
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/sample.schema.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((ROOT / "metadata/subsets.json").read_text(encoding="utf-8"))
SUBSETS = {entry["name"]: entry for entry in REGISTRY["subsets"]}
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
REFERENCE_FIELDS = {
    "long_audio_asr": "text",
    "long_audio_qa": "answers",
    "speaker_attributed_asr": "segments",
    "instruction_following": "constraints",
}


def check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("不允许 NaN 或 Infinity")
    if isinstance(value, dict):
        for item in value.values():
            check_finite(item)
    elif isinstance(value, list):
        for item in value:
            check_finite(item)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"重复的 JSON 字段：{key}")
        result[key] = value
    return result


def validate_sample(sample, media_root=None, require_reference=False):
    check_finite(sample)
    error = next(VALIDATOR.iter_errors(sample), None)
    if error:
        location = ".".join(map(str, error.absolute_path)) or "sample"
        raise ValueError(f"{location}: {error.message}")
    subset = SUBSETS[sample["subset"]]
    if sample["task"] != subset["task"]:
        raise ValueError("subset 与 task 不匹配")
    track = subset["tracks"].get(sample["track"])
    if track is None:
        raise ValueError("该子集不支持此 track")
    if sample["split"] == "example" and not sample["metadata"]["synthetic"]:
        raise ValueError("本格式的 example 必须显式标记 synthetic=true")
    media = sample["input"]["media"]
    by_id = {item["id"]: item for item in media}
    if len(by_id) != len(media):
        raise ValueError("media ID 重复")
    types = {item["type"] for item in media}
    if not set(track["required_media"]) <= types <= set(track["allowed_media"]):
        raise ValueError("媒体模态与 track 不匹配")
    messages = sample["input"]["messages"]
    if messages[-1]["role"] != "user":
        raise ValueError("最后一条输入消息必须是 user，不能包含待预测的回答")
    referenced = set()
    has_text = False
    for message in messages:
        for part in message["content"]:
            if part["type"] == "text":
                has_text = True
                continue
            item = by_id.get(part["media_id"])
            if item is None or item["type"] != part["type"]:
                raise ValueError("消息中的媒体引用不存在或类型不匹配")
            referenced.add(item["id"])
    if referenced != set(by_id):
        raise ValueError("存在未被消息引用的媒体")
    if sample["track"] == "audio_text" and not has_text:
        raise ValueError("audio_text 必须包含文本输入")
    for item in media:
        has_path = "path" in item
        has_url = "source_url" in item
        if has_path == has_url:
            raise ValueError("每个媒体必须且只能提供 path 或 source_url 之一")
        if has_url:
            url = item["source_url"]
            if not url.startswith("https://"):
                raise ValueError("source_url 必须是 https 公开下载地址")
            start = item["source_start_sec"]
            end = item["source_end_sec"]
            if not 0 <= start < end:
                raise ValueError("source_url 媒体必须提供 0<=source_start_sec<source_end_sec 的原始区间")
            if "duration_sec" in item and abs((end - start) - item["duration_sec"]) > 0.5:
                raise ValueError("source_end_sec-source_start_sec 应与 duration_sec 一致")
            continue
        path = item["path"]
        if any(char in path for char in ("\\", ":", "?", "#")) or any(
            part in ("", ".", "..") for part in path.split("/")
        ):
            raise ValueError("媒体必须使用安全的相对路径，不接受 URI 或路径穿越")
        if media_root is not None:
            root = Path(media_root).resolve()
            resolved = (root / path).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError("媒体路径或符号链接越出 media-root")
            if not resolved.is_file():
                raise ValueError(f"媒体不存在：{path}")
    if sample["track"] == "audiovisual":
        if any("sync_group" not in item or "time_offset_sec" not in item for item in media):
            raise ValueError("音视频必须显式提供 sync_group 和 time_offset_sec")
        if len({item["sync_group"] for item in media}) != 1:
            raise ValueError("当前音视频格式要求同一同步组")
        if max(item["time_offset_sec"] for item in media) >= min(
            item["time_offset_sec"] + item["duration_sec"] for item in media
        ):
            raise ValueError("音视频媒体在公共时间轴上没有交集")
    if sample["task"] in ("long_audio_asr", "speaker_attributed_asr"):
        if set(sample["languages"]["source"]) != set(sample["languages"]["target"]):
            raise ValueError("同语转写的 source 与 target 语言必须一致")
    reference = sample.get("reference")
    if reference is None:
        if require_reference:
            raise ValueError("缺少 reference")
        return
    if REFERENCE_FIELDS[sample["task"]] not in reference:
        raise ValueError("reference 缺少该 task 的必需标注")
    for segment in reference.get("segments", []):
        item = by_id.get(segment["media_id"])
        if item is None or item["type"] != "audio":
            raise ValueError("转写片段必须引用已声明的 audio")
        offset = item.get("time_offset_sec", 0)
        if not offset <= segment["start_sec"] < segment["end_sec"] <= offset + item["duration_sec"]:
            raise ValueError("转写片段时间无效或超出对应媒体的时间范围")
    constraints = reference.get("constraints", [])
    if len({item["id"] for item in constraints}) != len(constraints):
        raise ValueError("同一样本的约束 ID 重复")


def validate_file(path, media_root=None, require_reference=False):
    seen = set()
    count = 0
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                sample = json.loads(line, object_pairs_hook=unique_object)
                validate_sample(sample, media_root, require_reference)
                if sample["id"] in seen:
                    raise ValueError(f"重复样本 ID：{sample['id']}")
                seen.add(sample["id"])
                count += 1
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    if not count:
        raise ValueError("清单为空")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-reference", action="store_true")
    parser.add_argument("--check-media", action="store_true")
    parser.add_argument("--media-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        count = validate_file(args.manifest, args.media_root if args.check_media else None, args.require_reference)
    except (OSError, ValueError) as exc:
        print(f"校验失败：{exc}", file=sys.stderr)
        return 1
    print(f"校验通过：{count} 条样本；未执行模型推理、媒体解码或评分。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
