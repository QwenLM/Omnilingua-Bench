#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 MAXIFE-Omni 的 parquet 发布形态转换为 Omnilingua-Bench 的统一清单。

这是数据接入 Omnilingua-Bench 时用的一次性迁移工具，按 ``docs/data_format.md`` 的
Omnilingua-MaXIFE 约定，把逐语种的 ``<lang>/maxife_omni_<lang>.parquet`` 转成子集根
目录下的单个 ``Omnilingua-MaXIFE_v202609_public.jsonl``，并打印可直接登记进
``metadata/subsets.json`` 的 ``released_manifest`` 汇总。

依赖 pandas + pyarrow，只在迁移时需要；清单生成后校验器与评测脚本都只读 JSONL。

媒体文件名中的 ``:``（例如 ``fr_fr:0_turn_0.wav``）会被 ``tools/validate.py`` 判为非法
路径，因此按行把实际文件名里的 ``:`` 换成 ``_``（``--rename-media`` 会同步重命名磁盘
上的文件）。改名逐文件进行，不按 id 拼接路径：``ja`` 语言下的文件名前缀是 ``ja_jp``，
且存在 ``jp:18`` 这样与语言码不一致的 id 前缀。

用法：
    python tools/build_maxife_manifest.py --data-root . --rename-media
"""

import argparse
import hashlib
import json
import os
import sys
import wave
from collections import Counter
from pathlib import Path

import pandas as pd

MEDIA_ID = "instruction-0"
SUBSET = "Omnilingua-MaXIFE"
SCHEMA_VERSION = "0.1.0"
SUBSET_VERSION = "v202609"
SPLIT = "test"
LICENSE = "MIT (text) / CC BY-NC 4.0 (audio)"
MANIFEST_NAME = "Omnilingua-MaXIFE_v202609_public.jsonl"
DEFAULT_LANGS = ("fr", "id", "it", "ja", "ko", "pt", "tr")


def parquet_path(root, lang):
    return root / lang / f"maxife_omni_{lang}.parquet"


def sha256_file(path, chunk_size=1 << 20):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_media_path(path):
    """把文件名里的 ':' 换成 '_'，保持数据包根目录下的 POSIX 相对路径。"""
    return os.path.join(os.path.dirname(path), os.path.basename(path).replace(":", "_"))


def sample_id(lang, source_id):
    """MaxIFE-Omni 的 id 形如 fr:0 / jp:18；统一 id 用语言码加编号。"""
    return f"maxife-{lang}-{str(source_id).rsplit(':', 1)[-1]}"


def parse_kwargs(value):
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


def build_sample(row, lang, root):
    instruction_ids = list(row["instruction_id"])
    params = parse_kwargs(row["kwargs"])
    if len(instruction_ids) != len(params):
        raise ValueError(f"{row['id']}: instruction_id 与 kwargs 长度不一致")
    if len(set(instruction_ids)) != len(instruction_ids):
        raise ValueError(f"{row['id']}: 同一样本内约束 ID 重复")

    media_path = normalize_media_path(row["audio"])
    full_path = root / media_path
    if not full_path.is_file():
        raise ValueError(f"{row['id']}: 媒体不存在：{media_path}")
    with wave.open(str(full_path), "rb") as stream:
        duration = round(stream.getnframes() / stream.getframerate(), 3)
        sample_rate = stream.getframerate()

    prompt_text = row["prompt_text"]
    prompt_text = prompt_text if isinstance(prompt_text, str) and prompt_text.strip() else None
    track = "audio_text" if prompt_text else "audio"

    content = [{"type": "audio", "media_id": MEDIA_ID}]
    if prompt_text:
        content.append({"type": "text", "text": prompt_text})

    metadata = {
        "synthetic": False,
        "license": LICENSE,
        "source_id": str(row["id"]),
        "normalized_readable_text": str(row["normalized_readable_text"]),
    }
    tags = row["tags"]
    if isinstance(tags, str) and tags.strip():
        metadata["domain"] = tags

    return track, duration, {
        "schema_version": SCHEMA_VERSION,
        "id": sample_id(lang, row["id"]),
        "subset": SUBSET,
        "subset_version": SUBSET_VERSION,
        "split": SPLIT,
        "task": "instruction_following",
        "track": track,
        "languages": {"source": [lang], "target": [lang], "instruction": [lang]},
        "input": {
            "messages": [{"role": "user", "content": content}],
            "media": [{
                "id": MEDIA_ID,
                "type": "audio",
                "path": media_path,
                "duration_sec": duration,
                "sample_rate_hz": sample_rate,
            }],
        },
        "reference": {
            "constraints": [{"id": iid, "params": param} for iid, param in zip(instruction_ids, params)],
            "instruction_transcript": str(row["ori_prompt"]),
        },
        "metadata": metadata,
    }


def rename_media(root, rows):
    """按 parquet 的 audio 列重命名媒体文件。"""
    mapping, targets = {}, set()
    for raw in rows:
        new = normalize_media_path(raw)
        if new == raw:
            continue
        if new in targets:
            raise ValueError(f"改名后路径冲突：{new}")
        targets.add(new)
        if (root / new).exists():
            raise ValueError(f"改名后路径已被占用：{new}")
        mapping[raw] = new
    for old, new in mapping.items():
        os.rename(root / old, root / new)
    return len(mapping)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="子集根目录（含 <lang>/ 目录），默认本脚本所在目录的上一级")
    parser.add_argument("--langs", nargs="*", default=list(DEFAULT_LANGS), help="要转换的语言码")
    parser.add_argument("--rename-media", action="store_true",
                        help="同时重命名磁盘上的媒体文件（去掉文件名中的 ':'）")
    parser.add_argument("--summary-out", type=Path, default=None,
                        help="可选的 released_manifest 汇总输出路径（默认只打印到 stdout）")
    args = parser.parse_args()

    root = args.data_root.resolve()
    samples, language_counts, tracks, durations = [], Counter(), Counter(), []
    constraints, ids, built_from = set(), set(), []
    renamed = 0

    for lang in args.langs:
        source = parquet_path(root, lang)
        if not source.is_file():
            raise ValueError(f"缺少源文件：{source}")
        frame = pd.read_parquet(source)
        if args.rename_media:
            renamed += rename_media(root, frame["audio"].tolist())
        for _, row in frame.iterrows():
            track, duration, sample = build_sample(row, lang, root)
            if sample["id"] in ids:
                raise ValueError(f"id 重复：{sample['id']}")
            ids.add(sample["id"])
            samples.append(sample)
            language_counts[lang] += 1
            tracks[track] += 1
            durations.append(duration)
            constraints.update(item["id"] for item in sample["reference"]["constraints"])
        built_from.append({"file": f"{lang}/maxife_omni_{lang}.parquet",
                           "sha256": sha256_file(source)})
        print(f"{lang}: {language_counts[lang]} 条", file=sys.stderr)
    if renamed:
        print(f"重命名媒体文件 {renamed} 个", file=sys.stderr)

    # 逐语种连续输出，便于按语言顺序审阅
    manifest = root / MANIFEST_NAME
    with manifest.open("w", encoding="utf-8") as stream:
        for sample in samples:
            stream.write(json.dumps(sample, ensure_ascii=False) + "\n")

    summary = {
        "path": f"{root.name}/{MANIFEST_NAME}",
        "track": "audio/audio_text",
        "subset_version": SUBSET_VERSION,
        "split": SPLIT,
        "sample_count": len(samples),
        "sha256": sha256_file(manifest),
        "media_included": True,
        "media_reference": "path_relative_to_subset_root",
        "built_from": built_from,
        "language_count": len(language_counts),
        "language_counts": dict(sorted(language_counts.items())),
        "track_counts": dict(sorted(tracks.items())),
        "instruction_type_count": len(constraints),
        "duration_basis": f"{len(durations)} 条清单的 WAV 头解析时长；未经音频解码复核",
        "total_hours": round(sum(durations) / 3600, 5),
        "min_seconds": min(durations),
        "max_seconds": max(durations),
    }
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.summary_out:
        args.summary_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
