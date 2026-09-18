# 统一数据格式

版本：`0.1.0`。使用 UTF-8 JSONL，每行一个对象，无注释、不允许 NaN/Infinity。统一格式不依赖模型厂商或内部存储系统。

## 命名与任务

总项目名为 `Omnilingua-Bench`，`subset` 必须使用以下精确名称：

| subset | task | track | 参考标注 |
| --- | --- | --- | --- |
| Omnilingua-LongASR | long_audio_asr | audio | `reference.text` |
| Omnilingua-LongQA | long_audio_qa | audio_text | `reference.answers`，可选 rubric 与 evidence_text |
| Omnilingua-MSpeaker | speaker_attributed_asr | audio | `reference.segments` |
| Omnilingua-MSpeaker | speaker_attributed_asr | audiovisual | `reference.segments`；与 audio 轨道共用同一批源视频（source_url 即含画面的原始视频），覆盖同为 6 语种、297 条 |
| Omnilingua-MaXIFE | instruction_following | audio / audio_text | `reference.constraints` |

`track` 描述任务输入：音频任务可以附带固定文本指令；`audio_text` 表示文本问题或文本上下文也是任务内容。视频版本显式包含音频和视频流，不能仅靠 `.mp4` 扩展名推断使用了声音。

## 公共字段

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| schema_version | string | 格式版本，当前 `0.1.0` |
| id | string | 样本唯一 ID；同一发布版本跨分片唯一，保持稳定 |
| subset | string | 上表中四个子集名之一 |
| subset_version | string | 数据版本；示例为 `draft`，正式发布时冻结 |
| split | string | `example` / `dev` / `test` |
| task / track | string | 按上表绑定，不能把音频结果当作视频结果 |
| languages.source | string[] | 输入内容的语言代码；混语列出实际出现的语言 |
| languages.target | string[] | 任务要求的输出语言；不得根据模型预测反推 |
| languages.instruction | string[] | 指令／问题语言，和音频语言分别记录 |
| input.messages | object[] | 有序消息，包含 role 和有序 content 块 |
| input.media | object[] | 媒体清单，消息通过 media_id 引用 |
| reference | object | 评分用标注；隐藏答案的测试输入可省略 |
| metadata | object | synthetic、license 必填，另可放 domain、source_id、question_type、paired_id |

语言使用 BCP-47 风格代码，例如 `zh`、`en`、`pt-BR`；未知时用 `und`，不能把 `multilingual` 当语言代码。当前校验器仅检查语言代码语法，不认证实际音频语言。ASR 的 source 与 target 应一致；QA、指令遵循不得默认等同于翻译。

当前支持语种以 [子集目录](../metadata/subsets.json) 的 `supported_coverage` 为准：Omnilingua-LongASR 和 Omnilingua-LongQA 均为 `zh, en, es, fr, ja, ko, id, ru, ar, th`；Omnilingua-MSpeaker 音频轨道为 `es, fr, ja, ko, ru, th`；Omnilingua-MaXIFE 为 `fr, id, ja, ko, it, pt, tr`。`source_coverage` 仅保留原始清单统计，不代表全部纳入支持范围。格式校验与发布范围审核分开；合成示例可以使用支持范围以外的语言。

## 输入与媒体

文本块：`{"type":"text","text":"问题或指令"}`。
媒体块：`{"type":"audio","media_id":"audio-0"}`；视频使用 `video`。媒体基础结构预留 `image`，但首批四个子集不接受图像轨道；新增图像任务还需更新注册信息与 Schema。

媒体对象包含 `id`、`type`，并且必须且只能提供 `path`（本地文件）或 `source_url`（公开下载地址）之一；音频和视频另需 `duration_sec`。可选 `sha256`、`sample_rate_hz`、`fps`、`sync_group`、`time_offset_sec`。

- 本数据集不包含、不复制、不再分发任何原始音视频，仅提供索引引用。因此涉及无授权再分发的媒体一律使用 `source_url`，由使用者自行下载；这类样本不提供 `path`。
- `path` 是相对数据包根目录的 POSIX 路径，例如 `media/audio/sample.wav`。禁止绝对路径、`..`、内部 OSS 地址及带签名 URL。
- `source_url` 是 `https://` 公开地址（如原始视频页），并须配合 `source_start_sec`、`source_end_sec` 标出在原始媒体中的裁剪区间；`source_end_sec - source_start_sec` 应等于 `duration_sec`。校验器只检查 URL 语法与区间，不联网下载或核实内容可达性。
- 媒体应导出为实际送入模型的片段，`duration_sec` 是片段长度；原始裁剪起点可以写到 metadata，但不能混用原文件和片段的时间坐标。使用 `source_url` 时，片段的公共时间轴仍从 0 开始，`reference.segments` 的时间戳相对片段计。
- 片段在样本公共时间轴上的起点为 `time_offset_sec`（省略时为 0），因此媒体时间范围是 `[offset, offset + duration]`。
- Omnilingua-MSpeaker 音视频轨道的音频与视频都必须显式设置同一 `sync_group` 和各自 `time_offset_sec`。视频只提供视觉流，声音由 audio 块提供，避免将同一音轨输入两次。
- 校验器只能检查时间区间是否相交，不能验证实际音画同步；发布前还需媒体解码和人工抽检。
- 不应把完整样本对象作为模型请求：模型只接收 `input`，历史 assistant 消息只能是真正的对话历史，最后一条必须是 user。

## 各任务标注

### Omnilingua-LongASR

```json
{"reference":{"text":"完整的原语言参考转写。"}}
```

不混入译文、解释或模型生成结果；文本归一化由固定版本的评分器负责。

### Omnilingua-LongQA

```json
{
  "reference": {
    "answers": ["活动因暴雨而延期。"],
    "rubric": ["指出直接原因是暴雨，而不是人员不足。"],
    "evidence_text": "00:01:10 提到暴雨导致活动延期。"
  },
  "metadata": {"synthetic": true, "license": "TBD", "question_type": "reasoning"}
}
```

`answers` 支持多个合法答案；问题位于 `input.messages`，证据、评分细则只能位于 `reference`。

### Omnilingua-MSpeaker

```json
{
  "reference": {
    "segments": [
      {"media_id":"audio-0","start_sec":0.1,"end_sec":1.2,"speaker_id":"speaker_0","text":"你好。","language":"zh"},
      {"media_id":"audio-0","start_sec":0.8,"end_sec":1.8,"speaker_id":"speaker_1","text":"你好！","language":"zh"}
    ]
  }
}
```

时间戳以秒为单位、使用样本公共时间轴，允许不同说话人重叠。每段满足 `start_sec < end_sec`，且在对应音频时间范围内。说话人 ID 在样本内稳定，按首次出现顺序编号，不包含真实姓名。音频和视频的配对样本通过 `metadata.paired_id` 关联，但各自保留唯一 `id`。

### Omnilingua-MaXIFE

```json
{
  "reference": {
    "constraints": [
      {"id":"keywords:frequency","params":{"relation":"at_least","word_num":2,"word":"城市"}},
      {"id":"marks:wrap_in_quotes","params":{}}
    ],
    "instruction_transcript":"用双引号包裹摘要，并至少两次出现“城市”。"
  }
}
```

约束 ID 和参数保持与具体评分实现一致。`instruction_transcript` 可保留语音指令转写供裁判使用，但不能加入模型输入；已有文本上下文按原数据保留，不能将任务改造成纯文本指令遵循。当前格式工具不执行约束判定。

## 预测与结果格式建议

预测结果独立保存，按 `id` 连接样本；不要将预测写回参考答案。建议每行包含：

```json
{
  "id":"longaudioasr-demo-zh-0001",
  "subset_version":"draft",
  "run_id":"baseline-demo",
  "prediction":{"text":"这是一条格式示例。"},
  "status":"ok",
  "error":null
}
```

多说话人用 `prediction.segments`；空文本也是可记录的模型结果。`status` 可为 `ok`、`error`、`timeout`、`truncated`。一次运行还应记录模型版本、推理参数、提示词版本、媒体处理参数、清单校验值与评分器版本。基础设施失败应记录原因，不伪造正常分数。此预测格式为接口建议，尚无独立预测 Schema 或评分实现。

## 从已有清单迁移

| 旧字段 | 新字段／处理 |
| --- | --- |
| uuid / id | 加稳定子集前缀后写入 id，保留 metadata.source_id |
| task | 映射到标准 subset、task；旧领域后缀写到 metadata.domain |
| prompt 的嵌套模态块 | 转为 input.messages；抽出媒体到 input.media |
| audio / video 内部地址 | 经授权导出后换为相对 path；无授权再分发的公开媒体换为 source_url + source_start_sec/source_end_sec；禁止直接公开带签名 URL |
| lang / lang_code | 明确映射 languages.source；target 和 instruction 分别核实 |
| gt（转写） | reference.text 或解析为 reference.segments |
| gt（问答）、evidence_text | reference.answers、reference.evidence_text |
| instruction_id[i] + kwargs[i] | reference.constraints[i].id + params；先校验两个数组等长 |
| ori_prompt / normalized_readable_text | 仅作为评分所需的 reference.instruction_transcript，不自动加到 input |

当前不提供自动数据导出器，避免在版权和隐私审核前复制原数据。JSON Schema 校验不能代替版权审核、答案泄漏检查、标注质量审核或跨文件 ID 去重。
