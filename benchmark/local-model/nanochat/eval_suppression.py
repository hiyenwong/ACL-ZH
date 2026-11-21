#!/usr/bin/env python3
"""Evaluate a nanochat SFT arm on the frozen addition set.

Every generated token is visible and counted. There is no separate reasoning
channel: `prefix_chars` is exactly how much visible work the model emitted
before the answer, which is what "suppression" has to act on.

Run inside the nanochat environment, from the nanochat checkout:
  PYTHONPATH=<acl-zh>/benchmark/local-model/nanochat \
  .venv/bin/python <acl-zh>/benchmark/local-model/nanochat/eval_suppression.py \
      --model-tag d6-supp-trace --eval-set eval-set.jsonl --out runs/.../trace.json
"""
import argparse
import json
import re
from pathlib import Path

import torch
from nanochat.checkpoint_manager import load_model
from nanochat.common import compute_init, autodetect_device_type
from nanochat.engine import Engine

ANSWER_RE = re.compile(r"Answer:\s*(-?\d+)")
STEP_RE = re.compile(r"\d+\s*\+\s*\d+\s*=")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-tag", required=True)
    ap.add_argument("--source", default="sft")
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-tokens", type=int, default=160)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--device-type", default="")
    args = ap.parse_args()

    device_type = autodetect_device_type() if args.device_type == "" else args.device_type
    _, _, _, _, device = compute_init(device_type)
    model, tokenizer, meta = load_model(args.source, device, phase="eval", model_tag=args.model_tag)
    engine = Engine(model, tokenizer)

    bos = tokenizer.get_bos_token_id()
    user_start, user_end = tokenizer.encode_special("<|user_start|>"), tokenizer.encode_special("<|user_end|>")
    assistant_start, assistant_end = tokenizer.encode_special("<|assistant_start|>"), tokenizer.encode_special("<|assistant_end|>")

    rows = [json.loads(line) for line in Path(args.eval_set).read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[: args.limit]

    out_rows = []
    for i, row in enumerate(rows, 1):
        tokens = [bos, user_start]
        tokens.extend(tokenizer.encode(row["prompt"]))
        tokens.extend([user_end, assistant_start])
        generated = []
        with torch.no_grad():
            for token_column, _ in engine.generate(tokens, num_samples=1, max_tokens=args.max_tokens,
                                                   temperature=0.0):
                generated.append(token_column[0])
        ended = bool(generated) and generated[-1] == assistant_end
        if ended:
            generated = generated[:-1]
        text = tokenizer.decode(generated)

        matches = ANSWER_RE.findall(text)
        parsed = int(matches[-1]) if matches else None
        prefix = text.split("Answer:")[0] if "Answer:" in text else text
        prefix_lines = [ln for ln in prefix.splitlines() if ln.strip()]
        record = {
            "id": row["id"],
            "mode": row["mode"],
            "prompt": row["prompt"],
            "a": row["a"],
            "b": row["b"],
            "answer": row["answer"],
            "text": text,
            "parsed": parsed,
            "correct": parsed == row["answer"],
            "ended": ended,
            "generated_tokens": len(generated),
            "prefix_chars": len(prefix),
            "prefix_lines": len(prefix_lines),
            "has_step_pattern": bool(STEP_RE.search(text)),
        }
        out_rows.append(record)
        if i % 25 == 0:
            print(json.dumps({"done": i, "total": len(rows)}, ensure_ascii=False), flush=True)

    def summarize(records):
        n = len(records)
        if n == 0:
            return {}
        return {
            "n": n,
            "accuracy": round(sum(r["correct"] for r in records) / n, 4),
            "mean_generated_tokens": round(sum(r["generated_tokens"] for r in records) / n, 2),
            "mean_prefix_chars": round(sum(r["prefix_chars"] for r in records) / n, 2),
            "mean_prefix_lines": round(sum(r["prefix_lines"] for r in records) / n, 2),
            "leak_rate_prefix_chars_gt_0": round(sum(r["prefix_chars"] > 0 for r in records) / n, 4),
            "step_pattern_rate": round(sum(r["has_step_pattern"] for r in records) / n, 4),
            "ended_rate": round(sum(r["ended"] for r in records) / n, 4),
        }

    summary = {
        "model_tag": args.model_tag,
        "source": args.source,
        "max_tokens": args.max_tokens,
        "model_meta": {k: v for k, v in meta.items() if k in {"model_config", "user_config", "step"}},
        "overall": summarize(out_rows),
        "by_mode": {mode: summarize([r for r in out_rows if r["mode"] == mode]) for mode in ("direct", "trace")},
        "by_mode_and_size": {
            f"{mode}_{size}": summarize([
                r for r in out_rows
                if r["mode"] == mode and (("single" if r["a"] < 10 and r["b"] < 10 else "multi") == size)
            ])
            for mode in ("direct", "trace") for size in ("single", "multi")
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + "\n", encoding="utf-8")
    out.with_suffix(".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
