#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone scorer for the Omnilingua-MaXIFE subset of Omnilingua-Bench.

Dependencies: the Python standard library only. The samples are read from the subset's
unified manifest, `Omnilingua-MaXIFE_v202609_public.jsonl` (see docs/data_format.md in
the repository root); no pandas/pyarrow and no internal evaluation framework needed.

--------------------------------------------------------------------------
How to evaluate your model
--------------------------------------------------------------------------
1. Generate one response per sample. Give your (omni) model each sample's `input` only
   (the audio clip plus any text part) -- never `reference`, which holds the constraints
   and the spoken transcript for the scorer. Save the results as a JSONL file, one
   object per line, keyed by the sample `id` (bench prediction format):

       {"id": "maxife-fr-10", "subset_version": "v202609", "run_id": "baseline",
        "prediction": {"text": "...model output..."}, "status": "ok"}

   The legacy compact form is still accepted: {"id": "fr:10", "response": "..."}
   (`response` may also be named `gen`, and `prediction` may be a plain string).

2. Score the responses:

       # rule-based instructions only (no judge configured):
       python run_eval.py --pred responses.jsonl --out results.json --skip-judge

       # full scoring, including model-judged instructions
       # (style / tone / content / language_switch). Configure the judge model via
       # --judge-model or $JUDGE_MODEL; it is called through any OpenAI-compatible
       # /chat/completions endpoint, so point --judge-base-url at a gateway that serves it:
       python run_eval.py --pred responses.jsonl --out results.json \
           --judge-model your-judge-model \
           --judge-base-url "$JUDGE_BASE_URL" \
           --judge-api-key "$JUDGE_API_KEY"

   `--data` defaults to the subset root (the parent of this `eval/` folder), i.e. the
   directory holding the manifest plus one `<lang>/audio/` folder per language. It fails
   loudly if the manifest is missing or yields no samples, instead of reporting an
   empty run.

--------------------------------------------------------------------------
Scoring
--------------------------------------------------------------------------
Each sample carries one or more instructions. Every instruction is scored in [0, 1]:
  * rule-based  (keywords/marks/format/repeat/length/citation/emoji) -> verified by
    the checkers in maxife_utils/instructions.py
  * model-judged (style/tone/content/language_switch) -> an LLM judge returns one of
    {0, 0.7, 1.0} using the prompts in maxife_utils/prompt_template.py

Case-level metrics:
  acc           = mean of the sample's instruction scores
  perfect_score = 1 if every instruction scores >= 0.99 else 0
  wrong_score   = 1 if every instruction scores <= 0.01 else 0

Results are aggregated per instruction, per category, per language and overall.
"""
import argparse
import glob
import json
import os
import random
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maxife_utils.instructions import instruction_classes          # noqa: E402
from maxife_utils.prompt_template import PROMPT_TEMPLATES          # noqa: E402

JUDGE_PREFIXES = ("style:", "tone:", "content:", "language_switch:")
INVALID = -999999999  # marks a case whose judge call failed, so it can be retried/excluded


# --------------------------------------------------------------------------- #
# LLM judge (OpenAI-compatible /chat/completions via stdlib urllib)
# --------------------------------------------------------------------------- #
def make_judge(model, base_url, api_key, temperature=0.0, max_tokens=16384, timeout=120):
    url = base_url.rstrip("/") + "/chat/completions"

    def judge(prompt):
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        if api_key:
            req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    return judge


def parse_judge_score(text):
    """Map a judge reply to one of {0.0, 0.7, 1.0}; anything else -> 0.0."""
    if text is None:
        return None
    text = text.strip()
    if "\n" in text:
        text = text.split("\n")[-1]
    try:
        score = float(text)
    except ValueError:
        return 0.0
    return score if score in (0, 0.7, 1.0) else 0.0


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
DEFAULT_MANIFEST = "Omnilingua-MaXIFE_v202609_public.jsonl"


def resolve_manifest(data_root, manifest=None):
    """Locate the unified manifest for this subset; raise if it cannot be found."""
    if manifest:
        path = manifest if os.path.isabs(manifest) else os.path.join(data_root, manifest)
        if not os.path.isfile(path):
            raise SystemExit(f"error: manifest not found: {path}")
        return path
    path = os.path.join(data_root, DEFAULT_MANIFEST)
    if os.path.isfile(path):
        return path
    candidates = sorted(glob.glob(os.path.join(data_root, "Omnilingua-MaXIFE_v*.jsonl")))
    if not candidates:
        raise SystemExit(
            f"error: no unified manifest (Omnilingua-MaXIFE_v*.jsonl) in {data_root}; "
            f"pass --data/--manifest pointing at the subset root")
    return candidates[-1]


def language_of(sample):
    """Language of the sample: languages.source, falling back to metadata.source_id."""
    languages = sample.get("languages") or {}
    source = languages.get("source") or languages.get("instruction") or []
    if source:
        return source[0]
    source_id = str((sample.get("metadata") or {}).get("source_id", ""))
    return source_id.split(":", 1)[0] or "unknown"


def load_samples(data_root, langs=None, manifest=None):
    """Load samples from the subset's unified JSONL manifest.

    Rebuilds the internal view from the unified fields: `id`, language, the constraint
    ids/params, plus `track` and the media path (kept for logging/reference).
    """
    path = resolve_manifest(data_root, manifest)
    samples = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                sample = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"error: {path}:{lineno}: invalid JSON: {exc}")
            lang = language_of(sample)
            if langs and lang not in langs:
                continue
            constraints = (sample.get("reference") or {}).get("constraints") or []
            media = ((sample.get("input") or {}).get("media") or [{}])[0]
            samples.append({
                "id": sample["id"],
                "language": lang,
                "instruction_id": [c["id"] for c in constraints],
                "kwargs": [c.get("params") or {} for c in constraints],
                "track": sample.get("track"),
                "media": media.get("path"),
                # legacy upstream id (`fr:10`), so older prediction files still match
                "source_id": str((sample.get("metadata") or {}).get("source_id", "")),
            })
    if not samples:
        raise SystemExit(
            f"error: {path} yielded no samples"
            + (f" for --langs {' '.join(langs)}" if langs else ""))
    print(f"loaded {len(samples)} samples from {path}", file=sys.stderr)
    return samples


def prediction_text(value):
    """Extract the response text from a prediction value.

    Accepts the bench format ({"text": ...}) and the legacy compact form (a plain
    string, or a list whose first element is used).
    """
    if isinstance(value, dict):
        return value.get("text") or value.get("response") or ""
    if isinstance(value, list):
        return prediction_text(value[0]) if value else ""
    return value or ""


def load_predictions(path):
    """Read a prediction JSONL; returns (id -> text, Counter of statuses)."""
    preds, statuses = {}, Counter()
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"error: {path}:{lineno}: invalid JSON: {exc}")
            sid = d.get("id") or d.get("uuid") or d.get("key")
            if sid is None:
                raise SystemExit(f"error: {path}:{lineno}: prediction without an id")
            status = str(d.get("status", "ok"))
            statuses[status] += 1
            text = prediction_text(d.get("prediction"))
            if not text:
                text = prediction_text(d.get("response") if "response" in d else d.get("gen"))
            preds[str(sid)] = text or ""
    return preds, statuses


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def build_case(sample, response, judge, skip_judge):
    """Score rule-based instructions locally; collect this sample's model-judged prompts.

    Returns (scores, judge_tasks) where scores is a per-instruction list (None marks a
    slot awaiting a judge call) and judge_tasks is a list of (instr_index, prompt). The
    caller runs the judge calls (see score_one_sample).
    """
    lang = sample["language"]
    scores = []
    judge_tasks = []   # (index, prompt)
    for iid, kw in zip(sample["instruction_id"], sample["kwargs"]):
        cls = instruction_classes.get(iid)
        if cls is None:
            scores.append(0.0)
            continue
        inst = cls(lang)
        inst.build_description(**(kw or {}))
        if iid.startswith(JUDGE_PREFIXES):
            if judge is None:
                # --skip-judge -> count as 0; otherwise mark invalid (None) so it is excluded
                scores.append(0.0 if skip_judge else None)
                continue
            template = PROMPT_TEMPLATES[inst.__class__.__name__]
            prompt = template.format(instruction=inst.build_description(), response=response)
            scores.append(None)
            judge_tasks.append((len(scores) - 1, prompt))
        else:
            scores.append(inst.check_following(response))
    return scores, judge_tasks


def call_judge(judge, prompt):
    """One judge call with jittered exponential backoff (honors Retry-After on 429).

    Returns the parsed score, or None if all attempts failed.
    """
    for attempt in range(6):
        try:
            return parse_judge_score(judge(prompt))
        except Exception as e:              # transient / rate-limit error -> backoff & retry
            delay = min(30.0, 2.0 ** attempt) + random.uniform(0, 1)
            headers = getattr(e, "headers", None)
            if headers is not None:
                try:
                    delay = max(delay, float(headers.get("Retry-After", 0)))
                except (TypeError, ValueError):
                    pass
            time.sleep(delay)
    return None


def score_one_sample(sample, response, judge, skip_judge):
    """Score a single sample end-to-end: rule checks locally + its own judge calls.

    This is the unit of concurrency (one sample per worker). Returns a per-case dict.
    """
    scores, judge_tasks = build_case(sample, response, judge, skip_judge)
    for ii, prompt in judge_tasks:
        sc = call_judge(judge, prompt)
        if sc is None:
            print(f"[judge error] {sample['id']}", file=sys.stderr)
        scores[ii] = sc

    if any(x is None for x in scores):
        case_score, perfect, wrong = INVALID, INVALID, INVALID
    else:
        case_score = sum(scores) / max(1, len(scores))
        perfect = 1.0 if all(x >= 0.99 for x in scores) else 0.0
        wrong = 1.0 if all(x <= 0.01 for x in scores) else 0.0
    return {
        "id": str(sample["id"]), "language": sample["language"],
        "instruction_id": sample["instruction_id"],
        "scores": scores, "score": case_score, "perfect": perfect, "wrong": wrong,
    }


def aggregate(per_case):
    """per_case: list of dicts with language, instruction_id, scores, score, perfect, wrong."""
    res = {}
    instr_scores = defaultdict(list)
    for c in per_case:
        for iid, sc in zip(c["instruction_id"], c["scores"]):
            if sc is not None:
                instr_scores[iid].append(sc)

    by_instr = {}
    categories = sorted({i.split(":")[0] for i in instr_scores})
    for cat in categories:
        instrs = sorted(i for i in instr_scores if i.startswith(cat + ":"))
        for iid in instrs:
            v = instr_scores[iid]
            n = len(v)
            by_instr[f"{iid}/num"] = n
            by_instr[f"{iid}/acc"] = sum(v) / max(1, n)
            by_instr[f"{iid}/perfect_score"] = sum(1 for x in v if x >= 0.99) / max(1, n)
            by_instr[f"{iid}/wrong_score"] = sum(1 for x in v if x <= 0.01) / max(1, n)
        allv = [x for iid in instrs for x in instr_scores[iid]]
        n = len(allv)
        by_instr[f"{cat}/num"] = n
        by_instr[f"{cat}/acc"] = sum(allv) / max(1, n)
        by_instr[f"{cat}/perfect_score"] = sum(1 for x in allv if x >= 0.99) / max(1, n)
        by_instr[f"{cat}/wrong_score"] = sum(1 for x in allv if x <= 0.01) / max(1, n)
    res["by_instruction"] = by_instr

    # case-level, overall and per language
    def case_stats(cases):
        valid = [c for c in cases if c["score"] != INVALID]
        n = len(valid)
        return {
            "num_examples": len(cases),
            "num_valid": n,
            "acc": sum(c["score"] for c in valid) / max(1, n),
            "perfect_score": sum(c["perfect"] for c in valid) / max(1, n),
            "wrong_score": sum(c["wrong"] for c in valid) / max(1, n),
        }

    res["overall"] = case_stats(per_case)
    res["by_language"] = {}
    for lang in sorted({c["language"] for c in per_case}):
        res["by_language"][lang] = case_stats([c for c in per_case if c["language"] == lang])
    return res


def main():
    ap = argparse.ArgumentParser(description="Standalone Omnilingua-MaXIFE scorer")
    default_data = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--data", default=default_data,
                    help="subset root holding the unified manifest and <lang>/audio/ folders")
    ap.add_argument("--manifest", default=None,
                    help=f"manifest path (default: <data>/{DEFAULT_MANIFEST}, else the newest "
                         f"Omnilingua-MaXIFE_v*.jsonl in <data>)")
    ap.add_argument("--pred", required=True, help="JSONL of model responses, keyed by sample id")
    ap.add_argument("--out", default="results.json", help="where to write aggregated results")
    ap.add_argument("--per-case-out", default=None, help="optional JSONL of per-case scores")
    ap.add_argument("--langs", nargs="*", default=None, help="optional subset of language codes")
    ap.add_argument("--skip-judge", action="store_true",
                    help="score model-judged instructions as 0 instead of calling a judge")
    ap.add_argument("--judge-model", default=os.environ.get("JUDGE_MODEL", "your-judge-model"),
                    help="LLM judge model name (set --judge-model or $JUDGE_MODEL)")
    ap.add_argument("--judge-base-url", default=os.environ.get("JUDGE_BASE_URL", "https://api.openai.com/v1"),
                    help="OpenAI-compatible base URL serving the judge model")
    ap.add_argument("--judge-api-key", default=os.environ.get("JUDGE_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    ap.add_argument("--judge-workers", type=int, default=int(os.environ.get("JUDGE_WORKERS", "8")),
                    help="concurrent samples to score (default: 8)")
    ap.add_argument("--resume", action="store_true",
                    help="reuse valid cases already checkpointed in --per-case-out and only "
                         "score the rest (invalid/failed cases are retried)")
    args = ap.parse_args()

    samples = load_samples(args.data, args.langs, args.manifest)
    preds, statuses = load_predictions(args.pred)
    print(f"loaded {len(preds)} predictions from {args.pred}", file=sys.stderr)
    bad_status = {k: v for k, v in statuses.items() if k != "ok"}
    if bad_status:
        summary = ", ".join(f"{k}={v}" for k, v in sorted(bad_status.items()))
        print(f"WARNING: non-ok prediction statuses: {summary} "
              f"(they are still scored; empty text scores as wrong)", file=sys.stderr)

    judge = None
    if args.judge_model and not args.skip_judge:
        judge = make_judge(args.judge_model, args.judge_base_url, args.judge_api_key)
        print(f"judge enabled: {args.judge_model} @ {args.judge_base_url}", file=sys.stderr)
    else:
        n_judge = sum(1 for s in samples for i in s["instruction_id"] if i.startswith(JUDGE_PREFIXES))
        if n_judge and not args.skip_judge:
            print(f"WARNING: {n_judge} model-judged instructions but no judge configured; "
                  f"they will be marked invalid and excluded. Pass --judge-model to score them, "
                  f"or --skip-judge to count them as 0.", file=sys.stderr)

    # Resume: reuse valid cases already checkpointed in --per-case-out (invalid/failed
    # cases are retried). Without --resume the checkpoint file is started fresh.
    done = {}
    if args.per_case_out and args.resume and os.path.exists(args.per_case_out):
        with open(args.per_case_out, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("score") != INVALID:
                    done[rec["id"]] = rec
        print(f"resume: {len(done)} cases already scored, skipping them", file=sys.stderr)

    # Pair each sample with its prediction (by unified id, else by the legacy `fr:10`
    # id so pre-migration prediction files still work); skip samples with none or already done.
    to_score = []
    missing, matched_legacy = 0, 0
    matched_ids = set()
    for s in samples:
        sid = str(s["id"])
        legacy = s.get("source_id") or ""
        if sid in preds:
            text = preds[sid]
        elif legacy and legacy in preds and legacy not in matched_ids:
            text = preds[legacy]
            matched_legacy += 1
            matched_ids.add(legacy)
        else:
            missing += 1
            continue
        matched_ids.add(sid)
        if sid in done:
            continue
        to_score.append((s, text))
    if missing:
        print(f"WARNING: {missing} samples had no prediction and were skipped", file=sys.stderr)
    if matched_legacy:
        print(f"note: {matched_legacy} predictions matched by the legacy id "
              f"(e.g. `fr:10` instead of `maxife-fr-10`)", file=sys.stderr)
    sample_ids = {str(s["id"]) for s in samples} | {s.get("source_id") for s in samples}
    unmatched = sorted(k for k in preds if k not in sample_ids)
    if unmatched:
        preview = ", ".join(unmatched[:5]) + (" ..." if len(unmatched) > 5 else "")
        print(f"WARNING: {len(unmatched)} predictions matched no sample and were ignored "
              f"(e.g. {preview})", file=sys.stderr)

    # Score samples concurrently: one sample per worker. Each worker runs that sample's
    # rule-based checks locally and makes its own judge calls (see score_one_sample).
    # Every completed case is checkpointed to --per-case-out immediately, so an
    # interrupted run can be resumed and partial results can be inspected at any time.
    per_case = list(done.values())
    n_judge = sum(1 for s, _ in to_score for iid in s["instruction_id"]
                  if iid.startswith(JUDGE_PREFIXES))
    if judge is not None and n_judge:
        print(f"scoring {len(to_score)} samples ({n_judge} judge calls) with "
              f"{args.judge_workers} workers...", file=sys.stderr)
    ckpt = open(args.per_case_out, "a" if done else "w", encoding="utf-8") if args.per_case_out else None
    done_n = 0
    try:
        with ThreadPoolExecutor(max_workers=args.judge_workers) as ex:
            futures = [ex.submit(score_one_sample, s, r, judge, args.skip_judge)
                       for s, r in to_score]
            for fut in as_completed(futures):
                rec = fut.result()
                per_case.append(rec)
                if ckpt is not None:
                    ckpt.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    ckpt.flush()
                done_n += 1
                if done_n % 250 == 0:
                    print(f"  scored {done_n}/{len(to_score)} samples", file=sys.stderr)
    finally:
        if ckpt is not None:
            ckpt.close()

    n_invalid = sum(1 for c in per_case if c["score"] == INVALID)
    if n_invalid:
        print(f"WARNING: {n_invalid} cases had a failed judge call and are marked invalid",
              file=sys.stderr)

    results = aggregate(per_case)
    results["inputs"] = {
        "manifest": resolve_manifest(args.data, args.manifest),
        "prediction_file": args.pred,
        "prediction_status_counts": dict(sorted(statuses.items())),
        "samples_without_prediction": missing,
        "predictions_matched_by_legacy_id": matched_legacy,
        "unmatched_prediction_count": len(unmatched),
        "unmatched_prediction_ids": unmatched[:50],
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    # Rewrite the checkpoint cleanly (one line per id) now that scoring is complete.
    if args.per_case_out:
        with open(args.per_case_out, "w", encoding="utf-8") as fh:
            for c in per_case:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    o = results["overall"]
    print("\n===== Omnilingua-MaXIFE results =====")
    print(f"examples: {o['num_examples']} (valid {o['num_valid']})")
    print(f"acc: {o['acc']:.4f}  perfect: {o['perfect_score']:.4f}  wrong: {o['wrong_score']:.4f}")
    print("\nby language:")
    for lang, st in results["by_language"].items():
        print(f"  {lang}: acc={st['acc']:.4f} perfect={st['perfect_score']:.4f} "
              f"wrong={st['wrong_score']:.4f} (n={st['num_valid']})")
    print(f"\nfull results written to {args.out}")


if __name__ == "__main__":
    main()
