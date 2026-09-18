---
license: cc-by-nc-4.0
task_categories:
  - automatic-speech-recognition
  - audio-to-text
language:
  - ar
  - en
  - es
  - fr
  - id
  - ja
  - ko
  - ru
  - th
  - zh
tags:
  - long-form-audio
  - speech-recognition
  - multilingual
  - omni
  - evaluation
pretty_name: Omnilingua-LongASR
size_categories:
  - n<1K
---

# Omnilingua-LongASR

Omnilingua-LongASR is a **multilingual, long-form speech recognition** benchmark.
Each item is one long recording; the model listens to the whole audio and must
transcribe it into text in the **same language** (L → L, no translation).

- **135 items** across **10 languages**, **~129.94 hours** total
- Single-clip duration ranges **30.56 – 200.04 min** (median **~47.44 min**)
- Audio is **not** shipped: each item references a social-media source via
  `metadata.source_url` plus a `[source_start_sec, source_end_sec]` window
- The prompt is a fixed English instruction; `reference.text` is the full
  transcript

This is the `test` split of `Omnilingua-LongASR v202609`, one subset of the
Omnilingua-Bench suite (see the top-level `README.md`).

## Languages

**Table 1 — items per language**

| Language | Code | Items |
|----------|------|------:|
| Arabic | ar | 10 |
| English | en | 10 |
| Spanish | es | 10 |
| French | fr | 19 |
| Indonesian | id | 12 |
| Japanese | ja | 18 |
| Korean | ko | 14 |
| Russian | ru | 10 |
| Thai | th | 15 |
| Chinese | zh | 17 |
| **Total** | | **135** |

## Data layout

```
Omnilingua-LongASR/
├── OmniLingua-LongAudioASR_v202609_public.jsonl
└── README.md                 # this file
```

The JSONL carries **135** unique `id`s. Raw media is **not** included: each
item only references its source recording and the exact time window to cut.

### JSONL schema

| Field (JSON path) | Type | Description |
|-------------------|------|-------------|
| `id` | string | Stable item id, e.g. `omnilingua-longasr-test-ar-0001`. |
| `task` / `track` | string | Always `long_audio_asr` / `audio`. |
| `languages.source` | list | Source (= target) language code, e.g. `["ar"]`. `instruction` is `["en"]`. |
| `input.messages` | list | Chat payload: an `audio` part (`media_id`) plus the fixed English text instruction. |
| `input.media` | list | Media entry: `id` / `type` / `path` (e.g. `media/audio/<video_id>_<start>-<end>.wav`) / `duration_sec`. |
| `reference.text` | string | Full transcript in the source language. **Not** shown to the model. |
| `metadata.source_url` | string | Social-media URL of the source recording. |
| `metadata.source_start_sec` | float | Start of the clip inside the source video (seconds). |
| `metadata.source_end_sec` | float | End of the clip inside the source video (seconds). |
| `metadata.license` | string | `CC BY-NC 4.0`. |

### Loading

```python
import json
from pathlib import Path

root = Path("Omnilingua-LongASR")
rows = [json.loads(l) for l in (root / "OmniLingua-LongAudioASR_v202609_public.jsonl").open()]
assert len({r["id"] for r in rows}) == 135

row = rows[0]
lang = row["languages"]["source"][0]                 # "ar"
audio_path = row["input"]["media"][0]["path"]         # "media/audio/<video_id>_<start>-<end>.wav"
url = row["metadata"]["source_url"]                   # social-media URL
start, end = row["metadata"]["source_start_sec"], row["metadata"]["source_end_sec"]
gold = row["reference"]["text"]                       # full transcript, not for the model
```

The model sees **audio + instruction only**. Do not pass `reference.text` at
inference time.

## Preparing the audio

The release ships only annotations and relative media paths, **not** the audio
itself. Reconstruct each clip before evaluating:

1. **Download the source video** from `metadata.source_url` (a social-media URL),
   under the source platform's terms.
2. **Extract the audio** from the downloaded video (e.g. to 16 kHz mono WAV).
3. **Cut the clip** to `[metadata.source_start_sec, metadata.source_end_sec]`.
   The result should line up with `input.media[0].path`
   (`media/audio/<video_id>_<start>-<end>.wav`) and its `duration_sec`.

Example with `yt-dlp` + `ffmpeg`:

```bash
# 1) download the source video
yt-dlp -f bestaudio -o "src/<video_id>.%(ext)s" "<source_url>"

# 2+3) extract audio and cut to [start, end]  (mono, 16 kHz)
ffmpeg -i "src/<video_id>.<ext>" \
       -ss <source_start_sec> -to <source_end_sec> \
       -ac 1 -ar 16000 "media/audio/<video_id>_<start>-<end>.wav"
```

Then feed the cut clip to your (omni) model and save its transcript per item.

## Evaluation

The headline number is **WER ↓**, but a long-form transcript can fail in ways a
raw WER hides, so we **first tag failure modes**, then compute WER only on the
items where the model actually attempted a transcription. This matches the
top-level README ("WER ↓; empty-output / endless anomaly rates ↓").

### Failure modes (report these rates first)

| Mode | Definition | Effect on WER |
|------|------------|---------------|
| **empty** | Model returns nothing, or output length `< 1%` of the reference. WER is a degenerate constant `1.0` here, independent of the audio. | **Excluded** from WER. |
| **endless** | Not empty, but the model never stopped on its own and hit the output-length limit (runaway, usually repetition). WER is unbounded and one item can dominate the micro-average. | **Excluded** from WER. |

Priority is mutually exclusive: **empty > endless**. Both are removed from the
WER denominator.

### WER

WER is a **micro-average** over the valid items (all items **minus** empty and
endless): `WER = total_edit_distance / total_reference_length`. Report it
alongside the failure-mode counts, per language and overall:

- `wer` — micro-averaged over valid items
- `n_valid` / `n_total` — `n_valid = n_total − empty_num − endless_num`
- `empty_num` / `endless_num`

The authoritative scorer is the `longasr` task in `uniform-eval`
(`LongSpeechRecognitionTask`), which applies exactly the tags and aggregation
above.

## License

**CC BY-NC 4.0** — released for **research, non-commercial use only**.
License text: https://creativecommons.org/licenses/by-nc/4.0/legalcode.en

The **transcripts and annotations** are released under CC BY-NC 4.0. The
**source recordings** remain social-media videos: `source_url` is provided so you can
fetch and cut the audio under the source platform's terms. Do not redistribute the raw
audio; the copyright of the original content belongs to its respective owners.
