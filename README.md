<a id="english"></a>
# Omnilingua-Bench

**English** | [中文](#chinese)

**Multilingual, omni-modal evaluation of long-audio recognition, multi-speaker understanding, and instruction following.**

## Subsets

| Subset | Modality / Track | Task | Languages | Size | Key metrics | Released dataset (`split` · version) |
| --- | --- | --- | --- | --- | --- | --- |
| **Omnilingua-LongASR** | Audio → text; text task instruction included | Long-form same-language transcription | **10**: zh, en, ar, es, fr, id, ja, ko, ru, th | **134 items, ~127.44 h** | WER ↓; empty / endless anomaly rate ↓ | [`OmniLingua-LongAudioASR_v202609_public.jsonl`](Omnilingua-LongASR/OmniLingua-LongAudioASR_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-LongQA (MuLA-Bench)** | Audio + text question → text | Long-audio QA: factual/completeness, reasoning, temporal localization and long-range retrieval; semantic and acoustic evidence | **16**: zh, en, ar, de, es, fr, hi, id, it, ja, ko, pt, ru, th, tr, vi | **5,038 QA pairs, 1,732 distinct source recordings, 1,341 h** | Fixed-denominator accuracy (%) ↑; binary rubric | [`MuLA-Bench_v202609_public.jsonl`](MuLA-Bench/MuLA-Bench_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-MSpeaker** | `audio`: audio → text with speakers and timestamps | Multi-speaker transcription, speaker attribution and time alignment | **6**: es, fr, ja, ko, ru, th | **297 items, ~26.27 h** | tcpWER ↓, cpWER ↓, DER ↓ | [`Omnilingua-MSpeaker_v202609_public.jsonl`](Omnilingua-MSpeaker/Omnilingua-MSpeaker_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-MSpeaker** | `audiovisual`: audio-visual → text with speakers and timestamps | Vision-augmented multi-speaker transcription and attribution | **6**: es, fr, ja, ko, ru, th | **297 items, ~26.27 h** | tcpWER ↓, cpWER ↓, DER ↓ | Shares the same `source_url` video (with visuals) as the `audio` track; data as above |
| **Omnilingua-MaXIFE** | Speech instruction → text; some samples include text context | Multilingual complex instruction following | **7 mid-/high-resource languages**: fr, id, ja, ko, it, pt, tr | **5,387 synthesized-speech items** | Mean constraint score ↑, all-constraint satisfaction rate ↑ | [`Omnilingua-MaXIFE_v202609_public.jsonl`](Omnilingua-MaXIFE/Omnilingua-MaXIFE_v202609_public.jsonl) (with WAV) · `test` · `v202609` |
| **Omnilingua-AudioMC** | Multi-turn spoken dialogue: audio user turns → text reply (reference assistant history as text) | Multi-turn voice-conversation evaluation across 4 axes: inference & memory, instruction retention, self-coherence, voice editing; rubric-based LLM-judge grading | **10 + `en_tts` control arm**: en, zh, ja, es, fr, ru, de, it, th, vi | **3,894 conversations (354 × 11 arms)**, 1,404 rubric items per arm, ~140.64 h of user-turn audio | Instance pass rate ↑, rubric pass rate ↑ | [`Omnilingua-AudioMC_v202610_public.jsonl`](Omnilingua-AudioMC/Omnilingua-AudioMC_v202610_public.jsonl) (with WAV) · `test` · `v202610` |

## Highlights

- **Long-audio capability**: single clips in the released Omnilingua-LongASR range about **30.56–200.04 minutes**, focusing on transcription completeness and stability in long context.
- **Long-audio understanding**: Omnilingua-LongQA (MuLA-Bench) covers factual/completeness questions, reasoning, temporal localization and long-range retrieval. The final benchmark contains **5,038 open-ended QA pairs** across **16 languages and 8 domains**, over **1,732 in-the-wild source recordings** totaling **1,341 hours**. It combines **3,840 semantic questions** with **1,198 acoustic questions** grounded in naturally occurring events. Every Language × Domain cell contains exactly **30 semantic questions**, with a fixed task composition; acoustic coverage follows verified event availability. Original source recordings have a median duration of **36.7 minutes** and a mean of **46.5 minutes**.
- **Multi-speaker, real-world scenes**: the Omnilingua-MSpeaker audio track is drawn from public social-media videos; the released dataset has **297 items from 105 videos**, about 26.27 hours in total (`Omnilingua-MSpeaker/`). It provides video URLs and start/end ranges via `source_url`, ships no media files, and users must download them themselves. Reference annotations keep text, timestamps and anonymized speaker IDs.
- **Complex instruction composition**: the full Omnilingua-MaXIFE source list contains **11 categories, 47 constraint types** covering format, length, keywords, language switching, style, tone, citation and more; the current release supports 7 mid-/high-resource languages. It evaluates not only the answer content but also whether the instruction is followed.

## Quick start

Run from the repository root; requires Python 3.10+:

```bash
python -m pip install -r requirements.txt
python tools/validate.py Omnilingua-LongASR/OmniLingua-LongAudioASR_v202609_public.jsonl --require-reference
```

The released datasets use relative-path placeholders in `input.media[].path`; the repository **does not include the actual media**. The command above only validates structure and semantics. Once you have the media, you can check file existence:

```bash
python tools/validate.py your_manifest.jsonl --check-media --media-root /path/to/dataset
```

## Unified data format

One sample per line, with the common structure below; see the [format spec](docs/data_format.md) and [JSON Schema](schemas/sample.schema.json) for the full definition.

```json
{
  "schema_version": "0.1.0",
  "id": "longaudioasr-demo-zh-0001",
  "subset": "Omnilingua-LongASR",
  "subset_version": "draft",
  "split": "example",
  "task": "long_audio_asr",
  "track": "audio",
  "languages": {"source": ["zh"], "target": ["zh"], "instruction": ["zh"]},
  "input": {
    "messages": [{"role": "user", "content": [
      {"type": "audio", "media_id": "audio-0"},
      {"type": "text", "text": "请按原语言完整转写音频。"}
    ]}],
    "media": [{"id": "audio-0", "type": "audio", "path": "media/demo.wav", "duration_sec": 3.0}]
  },
  "reference": {"text": "这是一条格式示例。"},
  "metadata": {"synthetic": true, "license": "TBD", "domain": "example"}
}
```

## Project structure

```text
.
├── README.md
├── Omnilingua-LongASR/
│   └── OmniLingua-LongAudioASR_v202609_public.jsonl
├── MuLA-Bench/
│   └── MuLA-Bench_v202609_public.jsonl
├── Omnilingua-MSpeaker/
│   └── Omnilingua-MSpeaker_v202609_public.jsonl
├── docs/
│   ├── subsets.md               # Subset tasks, language coverage and evaluation criteria
│   └── data_format.md           # Unified format, prediction format and migration rules
├── metadata/subsets.json        # Subset registry and verified coverage
├── schemas/sample.schema.json   # Sample JSON Schema
├── tools/
│   └── validate.py              # Format, reference and time-range validation
├── requirements.txt
├── .gitlab-ci.yml
└── .gitignore
```

## Data usage statement and license

For third-party original audio/video (Omnilingua-MSpeaker, as well as media referenced by `source_url` in Omnilingua-LongASR and Omnilingua-LongQA (MuLA-Bench)), this dataset provides only index references and text annotation results. It does not include, copy or redistribute any such original audio/video content. It is for academic research only, not for commercial use, and the copyright of such original audio/video content belongs to its respective creators and rights holders. When accessing and using the referenced material, users must comply with the terms of service of the original content platforms.

The above indexes and text annotations are licensed under **CC BY-NC 4.0** (Attribution–NonCommercial 4.0 International). License text: https://creativecommons.org/licenses/by-nc/4.0/legalcode.en . This license applies only to the indexes and annotations provided by this repository and does not cover any rights in the original audio/video content.

Omnilingua-MaXIFE is released directly with the repository (`Omnilingua-MaXIFE/`) under a **dual license**: its text content (instructions, readable text, constraints) follows upstream MaXIFE's **MIT** license; the synthesized speech (WAV) is generated by our TTS and licensed under **CC BY-NC 4.0** (both license texts are in `LICENSE` under that directory). Neither belongs to the third-party original audio/video content referenced by URL above.

Omnilingua-AudioMC is likewise released with the repository (`Omnilingua-AudioMC/`): its indexes and text annotations are licensed under **CC BY-NC 4.0**; the task design, judge prompt and English source conversations derive from [ScaleAI/audiomc](https://huggingface.co/datasets/ScaleAI/audiomc) (MIT); the localized conversations and synthesized audio (the non-English arms and the `en_tts` control arm) were produced for this release.

## Citation

If Omnilingua-Bench or any of its sub-datasets helps your research, please cite:

```bibtex
@misc{omnilingua_bench_2026,
  title        = {Omnilingua-Bench: Multilingual Omni-modal Evaluation of Long Audio Recognition, Multi-speaker Understanding, and Instruction Following},
  author       = {{Alibaba Token Hub, Alibaba Group}},
  year         = {2026},
  howpublished = {\url{https://github.com/QwenLM/Omnilingua-Bench}}
}
```
```bibtex
@article{ge2026omnilingual,
  title={Omnilingual-MsASR: Benchmarking Multimodal, Multilingual, Long-Form Multi-Speaker ASR of Omni Large Language Models},
  author={Ge, Yuan and Zhang, Pei and Cheng, Xize and Mu, Lingzhou and Wang, Mingyang and Xu, Jin and Yang, Baosong and Gao, Shengxiang and Zhu, Jingbo and Yu, Zhengtao and others},
  journal={arXiv preprint arXiv:2610.29455},
  year={2026}
}
```

For standalone use of any subset, also refer to the documentation and license in its directory; the copyright of third-party original audio/video referenced by `source_url` belongs to their respective rights holders.

---

<a id="chinese"></a>
# Omnilingua-Bench

[English](#english) | **中文**

**面向多语言全模态模型的长音频识别、多说话人理解与指令遵循评测。**

## 子集一览

| 子集 | 模态／评测轨道 | Task | 支持语种 | 规模 | 主要评测指标 | 已发布数据集（`split` · 版本） |
| --- | --- | --- | --- | --- | --- | --- |
| **Omnilingua-LongASR** | 音频 → 文本；另有文本任务指令 | 长音频同语转写 | **10 种**：中、英、阿、西、法、印尼、日、韩、俄、泰 | **134 条，约 127.44 小时** | WER ↓；空输出、endless 等异常率 ↓ | [`OmniLingua-LongAudioASR_v202609_public.jsonl`](Omnilingua-LongASR/OmniLingua-LongAudioASR_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-LongQA (MuLA-Bench)** | 音频＋文本问题 → 文本 | 长音频问答：事实／完整性、推理、时间定位和长距离检索；语义与声学两类证据 | **16 种**：中、英、阿、德、西、法、印地、印尼、意、日、韩、葡、俄、泰、土、越 | **5,038 条问答，1,732 条不同源录音，1,341 小时** | 固定分母准确率（%）↑；二元 rubric | [`MuLA-Bench_v202609_public.jsonl`](MuLA-Bench/MuLA-Bench_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-MSpeaker** | `audio`：音频 → 带说话人和时间戳的文本 | 多说话人转写、说话人归属与时间对齐 | **6 种**：西、法、日、韩、俄、泰 | **297 条，约 26.27 小时** | tcpWER ↓、cpWER ↓、DER ↓ | [`Omnilingua-MSpeaker_v202609_public.jsonl`](Omnilingua-MSpeaker/Omnilingua-MSpeaker_v202609_public.jsonl) · `test` · `v202609` |
| **Omnilingua-MSpeaker** | `audiovisual`：音视频 → 带说话人和时间戳的文本 | 结合视觉的多说话人转写与归属 | **6 种**：西、法、日、韩、俄、泰 | **297 条，约 26.27 小时** | tcpWER ↓、cpWER ↓、DER ↓ | 与 `audio` 轨道共用同一 `source_url` 视频（含画面），数据同上 |
| **Omnilingua-MaXIFE** | 语音指令 → 文本；部分样本附文本上下文 | 多语言复杂指令遵循 | **7 种中高资源语言**：法、印尼、日、韩、意、葡、土 | **5,387 条合成语音** | 指令约束平均分 ↑、全部约束满足率 ↑ | [`Omnilingua-MaXIFE_v202609_public.jsonl`](Omnilingua-MaXIFE/Omnilingua-MaXIFE_v202609_public.jsonl)（含 WAV）· `test` · `v202609` |
| **Omnilingua-AudioMC** | 多轮语音对话：user 轮为音频 → 文本回复（assistant 历史为参考转写文本） | 多轮口语对话评测，覆盖 4 个能力轴：推断记忆、指令保持、自我一致、语音编辑；rubric LLM 裁判评分 | **10 种 + `en_tts` 控制组**：中、英、日、西、法、俄、德、意、泰、越 | **3,894 条对话（354 × 11 个条件）**，每条件 1,404 条 rubric、约 140.64 小时 user 轮音频 | Instance pass rate ↑、rubric pass rate ↑ | [`Omnilingua-AudioMC_v202610_public.jsonl`](Omnilingua-AudioMC/Omnilingua-AudioMC_v202610_public.jsonl)（含 WAV）· `test` · `v202610` |

## 核心特点

- **长音频能力**：Omnilingua-LongASR 已发布数据集中的单条音频区间约 **30.56–200.04 分钟**，关注长上下文中的转写完整性与稳定性。
- **长音频理解**：Omnilingua-LongQA (MuLA-Bench) 考察事实／完整性、推理、时间定位与长距离检索。最终基准包含 **5,038 条开放式问答**，覆盖 **16 种语言、8 个领域**，对应 **1,732 条真实场景源录音**，合计 **1,341 小时**。其中包括 **3,840 条语义题**和 **1,198 条基于自然声学事件的声学题**。每个“语言 × 领域”单元严格包含 **30 条语义题**，且任务组成固定；声学题数量由核实后的自然事件可用性决定。原始录音时长的中位数为 **36.7 分钟**，平均为 **46.5 分钟**。
- **多说话人与真实场景**：Omnilingua-MSpeaker 音频轨道取自社交媒体公开视频，已发布数据集共 **297 条、来自 105 个视频**，累计约 26.27 小时（`Omnilingua-MSpeaker/`）；数据集以 `source_url` 提供视频 URL 与起止区间，不含媒体文件，需使用者自行下载。参考标注保留文本、时间戳与匿名说话人 ID。
- **复杂指令组合**：Omnilingua-MaXIFE 原始全量清单包含 **11 类、47 种**约束，覆盖格式、长度、关键词、语言切换、风格、语气、引用等；当前支持 7 种中高资源语言，不只考察回答内容，也考察是否遵循指令。

## 快速开始

在本仓库根目录执行，要求 Python 3.10+：

```bash
python -m pip install -r requirements.txt
python tools/validate.py Omnilingua-LongASR/OmniLingua-LongAudioASR_v202609_public.jsonl --require-reference
```

已发布数据集的 `input.media[].path` 是相对路径占位，仓库**不包含真实媒体**。上面的命令只校验结构和语义；准备好媒体后可检查文件存在性：

```bash
python tools/validate.py your_manifest.jsonl --check-media --media-root /path/to/dataset
```

## 统一数据格式

每行一个样本，通用结构如下；完整定义见 [格式规范](docs/data_format.md) 和 [JSON Schema](schemas/sample.schema.json)。

```json
{
  "schema_version": "0.1.0",
  "id": "longaudioasr-demo-zh-0001",
  "subset": "Omnilingua-LongASR",
  "subset_version": "draft",
  "split": "example",
  "task": "long_audio_asr",
  "track": "audio",
  "languages": {"source": ["zh"], "target": ["zh"], "instruction": ["zh"]},
  "input": {
    "messages": [{"role": "user", "content": [
      {"type": "audio", "media_id": "audio-0"},
      {"type": "text", "text": "请按原语言完整转写音频。"}
    ]}],
    "media": [{"id": "audio-0", "type": "audio", "path": "media/demo.wav", "duration_sec": 3.0}]
  },
  "reference": {"text": "这是一条格式示例。"},
  "metadata": {"synthetic": true, "license": "TBD", "domain": "example"}
}
```

## 项目结构

```text
.
├── README.md
├── Omnilingua-LongASR/
│   └── OmniLingua-LongAudioASR_v202609_public.jsonl
├── MuLA-Bench/
│   └── MuLA-Bench_v202609_public.jsonl
├── Omnilingua-MSpeaker/
│   └── Omnilingua-MSpeaker_v202609_public.jsonl
├── docs/
│   ├── subsets.md               # 子集任务、语言覆盖与评测口径
│   └── data_format.md           # 统一格式、预测格式及迁移规则
├── metadata/subsets.json        # 子集注册信息与已核实覆盖
├── schemas/sample.schema.json   # 样本 JSON Schema
├── tools/
│   └── validate.py              # 格式、引用及时间范围校验
├── requirements.txt
├── .gitlab-ci.yml
└── .gitignore
```

## 数据使用声明与许可证

本数据集对第三方平台的原始音视频（Omnilingua-MSpeaker，以及 Omnilingua-LongASR、Omnilingua-LongQA (MuLA-Bench) 数据集中以 `source_url` 引用的媒体）仅提供索引引用和文本标注结果，不包含、不复制、不再分发任何该类原始音视频内容，仅用于学术研究，不用于商业用途，该类原始音视频内容的版权归其各自的创作者和权利人所有。使用者在访问和使用所引用的材料时，须自行遵守原始内容平台的服务条款。

上述索引与文本标注采用 **CC BY-NC 4.0**（署名—非商业性使用 4.0 国际）许可证。许可证文本：https://creativecommons.org/licenses/by-nc/4.0/legalcode.en 。该许可证仅适用于本仓库提供的索引与标注，不涉及原始音视频内容的任何权利。

Omnilingua-MaXIFE 直接随仓库发布（`Omnilingua-MaXIFE/`），采用**双许可**：其文本内容（指令、可朗读文本、约束）沿用上游 MaXIFE 的 **MIT** 许可证；合成语音（WAV）为我方 TTS 生成，采用 **CC BY-NC 4.0** 许可证（两份许可证文本见该目录下 `LICENSE`）。二者均不属于上述以 URL 引用的第三方原始音视频内容。

Omnilingua-AudioMC 同样随仓库发布（`Omnilingua-AudioMC/`）：索引与文本标注采用 **CC BY-NC 4.0**；任务设计、judge prompt 与英文源对话源自 [ScaleAI/audiomc](https://huggingface.co/datasets/ScaleAI/audiomc)（MIT）；本地化对话与合成音频（非英文各语言及 `en_tts` 控制组）为本发布制作。

## 引用

如果 Omnilingua-Bench 及其子集对你的研究有帮助，请引用：

```bibtex
@misc{omnilingua_bench_2026,
  title        = {Omnilingua-Bench: Multilingual Omni-modal Evaluation of Long Audio Recognition, Multi-speaker Understanding, and Instruction Following},
  author       = {{Alibaba Token Hub, Alibaba Group}},
  year         = {2026},
  howpublished = {\url{https://github.com/QwenLM/Omnilingua-Bench}}
}
```
```bibtex
@article{ge2026omnilingual,
  title={Omnilingual-MsASR: Benchmarking Multimodal, Multilingual, Long-Form Multi-Speaker ASR of Omni Large Language Models},
  author={Ge, Yuan and Zhang, Pei and Cheng, Xize and Mu, Lingzhou and Wang, Mingyang and Xu, Jin and Yang, Baosong and Gao, Shengxiang and Zhu, Jingbo and Yu, Zhengtao and others},
  journal={arXiv preprint arXiv:2610.29455},
  year={2026}
}
```

各子集若单独使用，请同时参考其目录下的说明与许可证；以 `source_url` 引用的第三方原始音视频，其版权归各自权利人所有。
