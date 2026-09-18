---
license:
- mit
- cc-by-nc-4.0
task_categories:
  - audio-to-text
language:
  - fr
  - id
  - it
  - ja
  - ko
  - pt
  - tr
tags:
  - instruction-following
  - omni
  - audio
  - multilingual
  - evaluation
pretty_name: Omnilingua-MaXIFE
---

# Omnilingua-MaXIFE

**Omnilingua-MaXIFE**（上游发布名 **MAXIFE-Omni**）是 [Omnilingua-Bench](../README.md)
的 `instruction_following` 子集：每条样本是一段 TTS 合成的语音指令，模型听完音频后
必须给出满足若干可验证约束（关键词、格式、长度、风格、语气等）的回答。

- 本子集 **7 种语言、5,387 条样本**（上游 MAXIFE-Omni 全量为 9 语 6,886 条，见下）
- 每条指令都是一段 **24 kHz 单声道 WAV**（`audio` 5,166 条；另 221 条在音频之外附文本上下文，`audio_text`）
- 每条样本带 **1 条或多条**约束，由规则检查器或 LLM 裁判判定
- 本子集是 Omnilingua-Bench 中**唯一随仓库附带媒体文件**的子集

## 与上游 MAXIFE-Omni 的关系

MAXIFE-Omni 是文本版 **MaXIFE** 的语音输入版本：

> MaXIFE: Multilingual and Cross-lingual Instruction Following Evaluation.
> ACL 2025. [arXiv:2506.01776](https://arxiv.org/abs/2506.01776) ·
> [github.com/OPPO-Mente-Lab/MaXIFE](https://github.com/OPPO-Mente-Lab/MaXIFE)

上游 MAXIFE-Omni 覆盖 **9 种语言、6,886 条**；Omnilingua-Bench 当前支持范围是其中
**7 种中高资源语言**（`fr, id, it, ja, ko, pt, tr`）共 **5,387 条**，英语（725 条）与
中文（774 条）不在本子集范围内。除下文说明的 id 方案与媒体文件名外，音频与约束标注
与上游一致。

构建流程（上游口径）：

1. **来源与单语过滤。** MaXIFE 同时包含*单语*与*跨语*（用英语作答）指令遵循样本，覆盖
   23 种语言。这里只保留**单语**变体，每种语言约 795 条候选。
2. **语言选择。** 上游为 9 种语言合成语音（本子集取其中的 7 种，见上）；其余 MaXIFE
   语言未合成，原因是 TTS 质量可能不佳。
3. **可朗读指令抽取。** 每条样本中能自然朗读的部分被抽出来合成为音频；过长的参考材料
   视为*不可朗读*，以文本形式保留（`prompt_text`），因此样本可能是音频＋文本的混合输入。
4. **TTS。** 用TTS 模型合成，**24 kHz、单声道**，每条样本
   随机分配音色。
5. **人工核验与过滤。** 每条合成音频都与其文本逐条人工比对，无法自然转成音频、或 TTS
   与文本不匹配的样本被剔除。

### 逐语言保留率

过滤（第 3–5 步）在本子集的 7 语范围内从 **5,484** 条候选保留 **5,387** 条（剔除 97 条，
**1.77%**）；上游全部 9 语为 7,074 条候选剔除 188 条（**2.66%**），差额来自不在本子集
范围内的 en（剔除率 8.81%）与 zh。

**表 1 — 本子集范围内的逐语言保留率**

| 语言 | 候选（单语） | 发布 | 剔除 | 剔除率 |
|------|------:|------:|------:|------:|
| fr | 795 | 755 | 40 | 5.03% |
| id | 776 | 773 | 3 | 0.39% |
| it | 774 | 766 | 8 | 1.03% |
| ja | 781 | 769 | 12 | 1.54% |
| ko | 781 | 781 | 0 | 0.00% |
| pt | 784 | 753 | 31 | 3.95% |
| tr | 793 | 790 | 3 | 0.38% |
| **合计** | **5,484** | **5,387** | **97** | **1.77%** |

### 对约束类型分布的影响

由于剔除量很小，约束类型分布基本保持不变。表 2 给出每种约束类别在该语言约束实例中
占比的变化（发布 − 候选，单位为百分点）。7 语范围内最大变化约为 1.1 pp（`fr` 的
`repeat`），超出本子集范围的英语 `format` 为 −2.6 pp。韩语与土耳其语几乎没有剔除，
分布不变。

**表 2 — 约束类型占比变化（发布 − 候选，百分点）**

| 语言 | keywords | marks | format | repeat | length | citation | emoji | style | tone | content | language_switch |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| fr | +0.0 | -0.9 | -0.3 | -1.1 | -0.0 | -0.0 | +0.2 | +0.7 | +0.7 | +0.5 | +0.2 |
| id | +0.1 | -0.1 | -0.1 | -0.1 | +0.0 | +0.0 | -0.0 | +0.1 | +0.1 | +0.0 | +0.0 |
| it | +0.0 | -0.1 | -0.3 | -0.1 | +0.0 | +0.0 | +0.0 | +0.2 | +0.2 | +0.1 | +0.1 |
| ja | +0.1 | -0.3 | -0.0 | -0.4 | +0.1 | -0.1 | +0.1 | +0.2 | +0.1 | +0.1 | +0.0 |
| ko | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| pt | -0.1 | -0.5 | -0.8 | -0.2 | +0.2 | -0.2 | -0.1 | +0.6 | +0.6 | +0.4 | +0.2 |
| tr | -0.1 | -0.1 | -0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |

## 目录结构

```text
Omnilingua-MaXIFE/
├── Omnilingua-MaXIFE_v202609_public.jsonl   # 统一格式清单，每行一个样本
├── fr/audio/*.wav                            # 各语言 24 kHz mono WAV（git LFS）
├── id/audio/  it/audio/  ja/audio/  ko/audio/  pt/audio/  tr/audio/
├── eval/                                     # 约束遵循评分脚本（见「评测」）
│   ├── run_eval.py
│   └── maxife_utils/
├── tools/build_maxife_manifest.py            # 由上游 parquet 生成上述清单的迁移工具
├── LICENSE
└── README.md
```

媒体路径相对本目录（即 `input.media[].path` 相对子集根目录）。**清单是唯一数据表示**：
上游的 7 个 `maxife_omni_<lang>.parquet` 已在迁移时转换为清单并删除，其 SHA-256 记录在
`metadata/subsets.json` 的 `released_manifest.built_from`。

### 逐语言样本数

| 语言 | 代码 | 样本数 |
|------|------|-------:|
| 法语 | fr | 755 |
| 印尼语 | id | 773 |
| 意大利语 | it | 766 |
| 日语 | ja | 769 |
| 韩语 | ko | 781 |
| 葡萄牙语 | pt | 753 |
| 土耳其语 | tr | 790 |
| **合计** | | **5,387** |

约束共 **47 种**，分属 11 类（`citation`、`content`、`emoji`、`format`、`keywords`、
`language_switch`、`length`、`marks`、`repeat`、`style`、`tone`）。

## 样本格式

字段定义见 [统一数据格式](../docs/data_format.md) 与
[JSON Schema](../schemas/sample.schema.json)。本子集特有约定：

- `id`：`maxife-<lang>-<n>`，如 `maxife-fr-10`（上游 id 为 `fr:10`，保留在
  `metadata.source_id`）。
- `track`：`audio_text`（221 条，音频之外附 `prompt_text` 文本上下文）或
  `audio`（5,166 条，仅音频）。
- `input.messages[0].content`：`{type:"audio", media_id:"instruction-0"}`，
  `audio_text` 样本再追加一个 `{type:"text", text:...}` 块。
- `input.media[0].path`：相对本目录的 WAV 路径，如 `fr/audio/fr_fr_5_c21f96.wav`；
  上游文件名中的 `:` 在迁移时改为 `_`（`fr_fr:5_c21f96.wav` → `fr_fr_5_c21f96.wav`）。
- `reference.constraints`：约束列表 `{id, params}`，由上游 `instruction_id[i]` 与
  `kwargs[i]` 逐项对应而来。
- `reference.instruction_transcript`：合成音频所用的完整指令文本（上游 `ori_prompt`）。
  **只给评分器，不能作为模型输入**。
- `metadata`：`source_id`、`normalized_readable_text`（上游该列的唯一保留处）、
  `domain`（上游 `tags`）、`license`、`synthetic`。

`maxife-fr-5`（取真实样本，`instruction_transcript` 与 `normalized_readable_text` 已截断）：

```json
{
  "schema_version": "0.1.0",
  "id": "maxife-fr-5",
  "subset": "Omnilingua-MaXIFE",
  "subset_version": "v202609",
  "split": "test",
  "task": "instruction_following",
  "track": "audio",
  "languages": {"source": ["fr"], "target": ["fr"], "instruction": ["fr"]},
  "input": {
    "messages": [{"role": "user", "content": [
      {"type": "audio", "media_id": "instruction-0"}
    ]}],
    "media": [{
      "id": "instruction-0",
      "type": "audio",
      "path": "fr/audio/fr_fr_5_c21f96.wav",
      "duration_sec": 42.6,
      "sample_rate_hz": 24000
    }]
  },
  "reference": {
    "constraints": [{"id": "marks:no_commas", "params": {}}],
    "instruction_transcript": "La Banque centrale européenne a décidé de lancer un nouveau programme …"
  },
  "metadata": {
    "synthetic": false,
    "license": "MIT (text) / CC BY-NC 4.0 (audio)",
    "source_id": "fr:5",
    "normalized_readable_text": "… Évitez d'utiliser des virgules tout au long de votre réponse.",
    "domain": "core"
  }
}
```

### 读取

清单是 JSONL，无需 pandas/pyarrow；媒体路径可直接与 `--media-root` 拼成实际文件：

```python
import json

with open("Omnilingua-MaXIFE_v202609_public.jsonl", encoding="utf-8") as stream:
    for line in stream:
        sample = json.loads(line)
        audio = sample["input"]["media"][0]["path"]        # 'fr/audio/fr_fr_5_c21f96.wav'
        constraints = sample["reference"]["constraints"]   # [{'id': 'keywords:frequency', 'params': {...}}, ...]
        messages = sample["input"]["messages"]             # 直接喂给模型；不要传 reference
```

### 校验

在仓库根目录执行（媒体由 git LFS 跟踪，需先 `git lfs pull`）：

```bash
python tools/validate.py Omnilingua-MaXIFE/Omnilingua-MaXIFE_v202609_public.jsonl \
    --require-reference --check-media --media-root Omnilingua-MaXIFE
```

## 指令与评分

每条样本按约束逐项打分，再在样本级别取平均。

- **规则检查器**（`keywords`、`marks`、`format`、`repeat`、`length`、`citation`、`emoji`）
  在 `eval/maxife_utils/instructions.py` 中程序化判定。
- **模型裁判**（`style`、`tone`、`content`、`language_switch`）用
  `eval/maxife_utils/prompt_template.py` 中的提示词交给 LLM 裁判，取值为 `{0, 0.7, 1.0}`。

> **可复现性。** 规则打分是确定性的；模型裁判的分数取决于裁判模型，换裁判可能让
> `style` / `tone` / `content` / `language_switch` 波动几个点（`style` 最敏感）。裁判模型可自行配置（`--judge-model` 或 `$JUDGE_MODEL`），报告含裁判类别的分数时应同时说明所用裁判。

样本级指标：

- `acc` — 该样本各约束得分的平均。
- `perfect_score` — 全部约束得分 ≥ 0.99 时为 1.0。
- `wrong_score` — 全部约束得分 ≤ 0.01 时为 1.0。

## 评测

`eval/run_eval.py` 是**自带评分器**（不再依赖 pandas/pyarrow，只用标准库 + 提交的
HTTP 客户端），bench 主仓不提供统一 scorer，本子集自带即可。

### 1. 生成预测

按 [预测与结果格式](../docs/data_format.md) 的约定，每条样本只接收 `input`（把音频与
可选的文本上下文喂给模型；**不要**传 `reference`），按 `id` 存一行 JSONL：

```jsonl
{"id": "maxife-fr-10", "subset_version": "v202609", "run_id": "baseline", "prediction": {"text": "...模型输出..."}, "status": "ok"}
{"id": "maxife-fr-2",  "prediction": {"text": "..."}, "status": "ok"}
```

兼容上游的简写形态：`{"id": "fr:10", "response": "..."}`（`response` 也可写作 `gen`、
`prediction` 字符串）。

### 2. 打分

```bash
# 只跑规则约束：
python Omnilingua-MaXIFE/eval/run_eval.py \
    --data Omnilingua-MaXIFE \
    --pred predictions.jsonl --out results.json --skip-judge

# 全部约束；模型裁判（style / tone / content / language_switch）需自行配置裁判模型，
# 走任意 OpenAI 兼容的 /chat/completions：
python Omnilingua-MaXIFE/eval/run_eval.py \
    --data Omnilingua-MaXIFE \
    --pred predictions.jsonl --out results.json \
    --judge-model your-judge-model \
    --judge-base-url "$JUDGE_BASE_URL" \
    --judge-api-key  "$JUDGE_API_KEY"
```

`--data` 默认本目录，清单缺失或读不到样本时会直接报错退出；`--langs fr id` 只评部分
语言，`--per-case-out cases.jsonl` 导出逐样本分数，`--resume` 可按 id 断点续跑。

脚本打印整体与逐语言的 `acc` / `perfect_score` / `wrong_score`，并在 `--out` 中写出
逐约束、逐类别的完整分解；预测中 `status` 非 `ok` 的条数与未匹配到样本的 id 会在结果
与 stderr 中汇总。

### 评分实现

- `eval/maxife_utils/instructions.py` — 规则检查器（仅标准库）。每个检查器用
  `build_description(**kwargs)` 构造，用 `check_following(response)` 打分；
  `instruction_classes` 是 `instruction_id → 类` 的映射。
- `eval/maxife_utils/prompt_template.py` — `PROMPT_TEMPLATES`，模型裁判的提示词，
  裁判回复被解析为 `{0, 0.7, 1.0}`。

逐样本：先给每条约束打分，再取 `acc` = 平均分、`perfect_score` = 全 ≥ 0.99 时为 1、
`wrong_score` = 全 ≤ 0.01 时为 1。裁判调用失败时该样本标记为无效，不计入平均。

## 音频

全部音频由TTS 模型从每条指令的可朗读部分合成：24 kHz、单声道
WAV，每条样本随机分配音色。5,387 个 WAV 随仓库以 git LFS 发布。

## 许可证

本子集采用**双许可**：

- **文本内容**（指令、可朗读文本、约束等，源自上游 [MaXIFE](https://github.com/OPPO-Mente-Lab/MaXIFE)）沿用其 **MIT** 许可证。
- **合成语音**（5,387 个 WAV，由我方 TTS 生成）采用 **CC BY-NC 4.0**（署名—非商业性使用 4.0 国际），与 Omnilingua-Bench 其余子集的媒体许可一致。

两份许可证文本见 `LICENSE`（MIT 全文；CC BY-NC 4.0 见 https://creativecommons.org/licenses/by-nc/4.0/legalcode.en ）。


## 引用

使用 Omnilingua-MaXIFE 时请引用其上游 MaXIFE 基准：

```bibtex
@inproceedings{maxife2025,
  title     = {MaXIFE: Multilingual and Cross-lingual Instruction Following Evaluation},
  author    = {OPPO Mente Lab},
  booktitle = {Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL)},
  year      = {2025},
  eprint    = {2506.01776},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2506.01776}
}
```
