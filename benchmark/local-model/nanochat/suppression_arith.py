#!/usr/bin/env python3
"""Synthetic addition task with a controlled visible-scratchpad treatment.

Used as an external SFT mixture for nanochat (see PREREG-NANOCHAT-SUPPRESSION-V0.1.md).

Both arms see identical user prompts and identical item order. They differ only in
the assistant target on items whose prompt asks for work to be shown:

  arm "trace"  -> trace prompt is answered with a decomposition + "Answer: N"
                  direct prompt is answered with "Answer: N"
  arm "direct" -> every prompt is answered with "Answer: N"

Because nanochat's chat template has a single visible assistant channel, every
token of the trace is supervised and countable. There is no hidden reasoning
channel to inspect or to suppress.
"""
import json
import os
import random
from pathlib import Path

from tasks.common import Task, TaskMixture

TRAIN_ITEMS = 24000
EVAL_ITEMS = 200
TRAIN_SEED = 20261121
EVAL_SEED = 771721

TRACE_PROMPT = "Compute {a}+{b}. Show your work, then give the final answer."
DIRECT_PROMPT = "Compute {a}+{b}. Do not show your work. Give only the final answer."

ARM = os.environ.get("NANOCHAT_SUPP_ARM", "trace")
assert ARM in {"trace", "direct"}, ARM


def _draw(rng):
    """Half single-digit pairs, half pairs with at least one two-digit operand."""
    if rng.random() < 0.5:
        return rng.randint(0, 9), rng.randint(0, 9)
    while True:
        a, b = rng.randint(0, 49), rng.randint(0, 49)
        if a >= 10 or b >= 10:
            return a, b


def make_items(n, seed):
    rng = random.Random(seed)
    items = []
    for i in range(n):
        a, b = _draw(rng)
        # Deterministic instruction assignment: alternate, offset per index.
        mode = "trace" if (i % 2 == 0) else "direct"
        items.append({"id": f"{seed}-{i:05d}", "a": a, "b": b, "mode": mode, "answer": a + b})
    return items


def trace_target(item):
    a, b = item["a"], item["b"]
    hi_a, lo_a = (a // 10) * 10, a % 10
    hi_b, lo_b = (b // 10) * 10, b % 10
    return (
        f"{a} + {b}\n"
        f"{hi_a} + {hi_b} = {hi_a + hi_b}\n"
        f"{lo_a} + {lo_b} = {lo_a + lo_b}\n"
        f"{hi_a + hi_b} + {lo_a + lo_b} = {a + b}\n"
        f"Answer: {a + b}"
    )


def direct_target(item):
    return f"Answer: {item['answer']}"


def prompt_for(item, mode):
    template = TRACE_PROMPT if mode == "trace" else DIRECT_PROMPT
    return template.format(a=item["a"], b=item["b"])


def assistant_for(item):
    if ARM == "trace" and item["mode"] == "trace":
        return trace_target(item)
    return direct_target(item)


class SuppressionArith(Task):
    eval_type = "generative"

    def __init__(self, split, **kwargs):
        super().__init__(**kwargs)
        assert split in {"train", "eval"}
        self.split = split
        self.items = make_items(TRAIN_ITEMS if split == "train" else EVAL_ITEMS,
                                TRAIN_SEED if split == "train" else EVAL_SEED)

    def num_examples(self):
        return len(self.items)

    def get_example(self, index):
        item = self.items[index]
        return {
            "messages": [
                {"role": "user", "content": prompt_for(item, item["mode"])},
                {"role": "assistant", "content": assistant_for(item)},
            ]
        }


def build_train_tasks():
    print(f"[suppression-arith] arm={ARM} train_items={TRAIN_ITEMS}")
    return [SuppressionArith(split="train")]


def build_val_dataset():
    # Only used when --eval-every > 0; the frozen run disables it.
    return TaskMixture([SuppressionArith(split="eval")])


def write_eval_set(path):
    """Freeze the exact evaluation prompts (both instruction modes) for the eval script."""
    items = make_items(EVAL_ITEMS, EVAL_SEED)
    rows = []
    for item in items:
        for mode in ("direct", "trace"):
            rows.append({
                "id": item["id"],
                "mode": mode,
                "prompt": prompt_for(item, mode),
                "a": item["a"],
                "b": item["b"],
                "answer": item["answer"],
            })
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                          encoding="utf-8")
    print(f"[suppression-arith] wrote {len(rows)} eval prompts to {path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-eval-set", required=True)
    args = ap.parse_args()
    write_eval_set(args.write_eval_set)
