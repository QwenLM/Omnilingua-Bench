---
license: cc-by-nc-4.0
task_categories:
  - audio-text-to-text
  - question-answering
language:
  - ar
  - de
  - en
  - es
  - fr
  - hi
  - id
  - it
  - ja
  - ko
  - pt
  - ru
  - th
  - tr
  - vi
  - zh
tags:
  - long-form-audio
  - multilingual
  - audio-understanding
  - omni
  - evaluation
  - question-answering
  - acoustic-events
pretty_name: MuLA-Bench
size_categories:
  - 1K<n<10K
---

# MuLA-Bench

**MuLA-Bench: A Multilingual Long-form Audio Understanding Benchmark via Multi-Tier Auditing**

MuLA-Bench is a **multilingual, long-form audio understanding** benchmark. Each
item is a question over a naturally occurring long recording; the model listens
to the source audio and answers from spoken content, natural acoustic events, or both.

- **5,029 questions** over **1,768 source recordings** (**~1,371 hours**)
- **16 languages × 8 domains**, with **30 semantic questions per cell** 
- Two evidence tracks: **semantic** (spoken content) and **acoustic** (natural sound events)
- Four operations: **factual / reasoning / temporal / long-range**
- Multi-tier construction: program gates, transcript–audio ablation, and expert listening

## Why this benchmark

Most audio QA sets are short clips, English-centric, or use synthesized /
injected sounds. In MuLA-Bench **the same long recording** can support different
operations on different evidence types — a spoken fact, a natural applause, a
clock-grounded event, or two cues tens of minutes apart. Overall accuracy on the
5,029-item freeze is therefore not a single skill score: two models can match on
the headline and still have opposite semantic / acoustic profiles.



### Per-language inventory

Semantic coverage is **30 × 8 domains = 240 / language**. Acoustic
coverage is **not** forced to a flat 10 / cell (one cell, `tr/howto`, is empty).

**Table 1 — questions and source recordings by language**

| Language | Code | Questions | Sources |
|----------|------|----------:|--------:|
| Arabic | ar | 313 | 110 |
| German | de | 304 | 119 |
| English | en | 347 | 126 |
| Spanish | es | 316 | 120 |
| French | fr | 338 | 98 |
| Hindi | hi | 290 | 125 |
| Indonesian | id | 324 | 128 |
| Italian | it | 304 | 88 |
| Japanese | ja | 311 | 101 |
| Korean | ko | 333 | 101 |
| Portuguese | pt | 306 | 106 |
| Russian | ru | 308 | 117 |
| Thai | th | 309 | 124 |
| Turkish | tr | 301 | 107 |
| Vietnamese | vi | 288 | 82 |
| Chinese | zh | 337 | 116 |
| **Total** | | **5,029** | **1,768** |

### Task × evidence

**Table 2 — official freeze by operation and evidence type**

| Operation (`task_type`) | Semantic | Acoustic | Total |
|-------------------------|--------:|--------:|------:|
| Factual / completeness (`completeness_fact`) | 1,024 | 865 | 1,889 |
| Reasoning (`reasoning`) | 1,023 | 121 | 1,144 |
| Temporal (`time_localization`) | 894 | 111 | 1,005 |
| Long-range (`long_range`) | 895 | 96 | 991 |
| **Total** | **3,836** | **1,193** | **5,029** |

Domains (question counts): lifestyle 674, knowledge 640, news 637, belief 635,
narrative 630, product 628, entertainment 594, howto 591.

Source duration is the original recording length (median **37 min**; four
sources exceed 3 h, max 3 h). Evaluation input is the **full source**,
except the four post-3 h items, which use a predefined later-stage 3 h window
that covers all gold evidence.

## Data layout

```
mula-bench/
├── MuLA-Bench_v202609_public.jsonl
└── README.md                 # this file
```

Official evaluation uses `MuLA-Bench_v202609_public.jsonl` (**5,029** unique
`id`s). 

### JSONL schema

| Field (JSON path) | Type | Description |
|-------------------|------|-------------|
| `id` | string | Stable item id, e.g. `nonac\|ar\|belief\|-aR600r70zQ\|80b787bc2ad8`. |
| `languages.source` | list | Source language code(s), e.g. `["ar"]`. `target` / `instruction` mirror it. |
| `input.messages` | list | Chat payload: an `audio` part (`media_id`) plus the `text` question in the source language. |
| `input.media` | list | Media entries with `id` / `type` / `path` (e.g. `media/audio/<video_id>.mp3`) / `duration_sec`. |
| `reference.answers` | list | Reference answer(s). **Not** shown to the model. |
| `reference.evidence_text` | string | Timestamped evidence used to write the item. **Not** shown to the model. |
| `metadata.video_id` | string | Social-media / source recording id. |
| `metadata.source_url` | string | Social-media URL of the source recording. |
| `metadata.topic` | string | Domain: `knowledge` / `howto` / `narrative` / `entertainment` / `lifestyle` / `news` / `product` / `belief`. |
| `metadata.cell` | string | `lang/topic`, e.g. `ar/belief`. |
| `metadata.modality` | string | `semantic` (spoken content) or `acoustic` (natural sound). |
| `metadata.task_type` | string | `completeness_fact` / `reasoning` / `time_localization` / `long_range`. |
| `metadata.judge_type` | string | Scoring route: `single_fact` / `reasoning` / `multi_slot` / `exhaustive_list` / `time_point_program` / `time_order`. |
| `metadata.difficulty` | string | `easy` / `hard`. |

### Loading

```python
import json
from pathlib import Path

root = Path("mula-bench")
rows = [json.loads(l) for l in (root / "MuLA-Bench_v202609_public.jsonl").open()]
assert len({r["id"] for r in rows}) == 5029

row = rows[0]
qid = row["id"]
video_id = row["metadata"]["video_id"]
question = next(c["text"] for c in row["input"]["messages"][0]["content"]
                if c["type"] == "text")
gold = row["reference"]["answers"][0]
modality = row["metadata"]["modality"]   # "semantic" or "acoustic"
```

The model sees **audio + question only**. Do not pass `reference.evidence_text`,
`reference.answers`, or gold timestamps at inference time.

## Evaluation

Headline metric is **accuracy on the official 5,029**, with a **fixed
denominator**. Unanswered items, refusals, and persistent input-limit failures
count as 0. Coverage (valid responses / 5,029) is diagnostic only.

### Fair input

1. **Canonical input** is the full source recording. Only the four post-3 h
   items (`Hgi8zNQnEa8`) use the official later-stage 3 h window. Format /
   bitrate conversion is allowed if it does **not** drop content.
2. **Local models** that cannot ingest the full canonical input take the
   **longest native prefix from the start of that input**. No
   evidence-aware or listen-point crop.
3. Gold-aware windows (e.g. a 46.7 min clip centered on the evidence) are
   invalid and scored 0.

Slice scores use the official slice size as the denominator
(semantic 3,836, acoustic 1,193, and the four operations above).

### Judge

All official scores use **`judge_scripts`** with **`llm`**, routed by
`judge_type`:

| Route | What is checked |
|-------|-----------------|
| `single_fact` | One checkable claim against the gold. |
| `reasoning` | Multi-evidence conclusion. |
| `multi_slot` | Several slots must all match. |
| `exhaustive_list` | Full list, no missing / extra items. |
| `time_order` | Mention order of timed events (no second-level clock tolerance). |
| `time_point_program` | Event match **plus** a programmatic clock check. |

`time_point_program` uses a fixed rule (`pair_ok`, `TOL = 3.0 s`):

- point vs. point: `|pred − gold| ≤ 3 s`
- gold interval, predicted point: point inside `[g0−3, g1+3]`
- gold point, predicted interval: predicted width **≤ 10 s** and the widened
  interval covers the gold point
- predicted interval **> 10 s** is not accepted as a short-interval wrap

Report the judge (`llm`) and this time rule with any number you
publish. A different judge can move the LLM-judged routes.

### Scoring a prediction file

Save one JSONL row per official `id`:

```jsonl
{"id": "nonac|ar|belief|-aR600r70zQ|80b787bc2ad8", "response": "...model output..."}
```

(`response` may also be named `gen` or `prediction`.) Then run the official
`judge_v3` / `reeval_judge_v1` pipeline on the 5,029-id set. Items missing
from the prediction file are scored 0.


## License

**CC BY-NC 4.0** — released for **research, non-commercial use only**.
License text: https://creativecommons.org/licenses/by-nc/4.0/legalcode.en

The **questions, answers, and audit labels** are released under CC BY-NC 4.0.
The **source recordings** remain social-media videos: `video_id` is provided so you
can fetch audio under the source platform’s terms. Redistributing raw social-media audio may
be restricted; do not treat the audio itself as CC BY-NC 4.0.

## Citation

If you use MuLA-Bench, please cite:

```bibtex
@article{yang2026mulabench,
  title   = {MuLA-Bench: A Multilingual Long-form Audio Understanding Benchmark via Multi-Tier Auditing},
  author  = {Yang, Zeyu and Zhang, Xinyu and Bi, Zibo and Zhang, Pei and Cheng, Xize and Xu, Jin and Yang, Baosong and Nakamura, Satoshi},
  year    = {2026}
}
```
