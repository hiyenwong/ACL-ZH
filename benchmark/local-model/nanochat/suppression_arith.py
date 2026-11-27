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

try:
    from tasks.common import Task, TaskMixture
except ModuleNotFoundError:  # Allows standalone eval generation and unit tests outside nanochat.
    class Task:
        def __init__(self, **kwargs):
            pass

    class TaskMixture:
        def __init__(self, tasks):
            self.tasks = tasks

TRAIN_ITEMS = 24000
EVAL_ITEMS = 200
EVAL_SINGLE_PAIRS = 50
EVAL_MULTI_PAIRS = EVAL_ITEMS - EVAL_SINGLE_PAIRS
SPLIT_SEED = 20261127
TRAIN_SEED = 20261121
EVAL_SEED = 771721

# Amendment A3: duplicate the mixture to give direct arms more optimizer steps
# within one dataloader epoch (the dataloader ends training at epoch end).
_train_items_override = int(os.environ.get("NANOCHAT_SUPP_TRAIN_ITEMS", "0"))
if _train_items_override > 0:
    assert _train_items_override % TRAIN_ITEMS == 0, _train_items_override

TRACE_PROMPT = "Compute {a}+{b}. Show your work, then give the final answer."
DIRECT_PROMPT = "Compute {a}+{b}. Do not show your work. Give only the final answer."

ARM = os.environ.get("NANOCHAT_SUPP_ARM", "trace")
assert ARM in {"trace", "direct"}, ARM


def partition_operand_pairs(split_seed=SPLIT_SEED):
    """Deterministically partition single- and multi-digit operand pairs into disjoint train/eval pools."""
    single_pairs = [(a, b) for a in range(10) for b in range(10)]
    multi_pairs = [(a, b) for a in range(50) for b in range(50) if a >= 10 or b >= 10]
    rng = random.Random(split_seed)
    rng.shuffle(single_pairs)
    rng.shuffle(multi_pairs)
    eval_single = single_pairs[:EVAL_SINGLE_PAIRS]
    train_single = single_pairs[EVAL_SINGLE_PAIRS:]
    eval_multi = multi_pairs[:EVAL_MULTI_PAIRS]
    train_multi = multi_pairs[EVAL_MULTI_PAIRS:]
    train_pairs = set(train_single) | set(train_multi)
    eval_pairs = set(eval_single) | set(eval_multi)
    assert not (train_pairs & eval_pairs), "train and eval operand pairs must be disjoint"
    return (train_single, train_multi), (eval_single, eval_multi)


def _draw_from_pools(rng, single_pool, multi_pool):
    """Half single-digit pairs, half pairs with at least one two-digit operand."""
    if rng.random() < 0.5:
        return rng.choice(single_pool)
    return rng.choice(multi_pool)


def make_items(n, seed, split="train", split_seed=SPLIT_SEED):
    assert split in {"train", "eval"}, split
    (train_single, train_multi), (eval_single, eval_multi) = partition_operand_pairs(split_seed)
    rng = random.Random(seed)
    items = []
    if split == "eval":
        eval_pool = list(eval_single) + list(eval_multi)
        rng.shuffle(eval_pool)
        assert n <= len(eval_pool), f"Requested {n} unique eval items, only {len(eval_pool)} available"
        for i, (a, b) in enumerate(eval_pool[:n]):
            mode = "trace" if (i % 2 == 0) else "direct"
            items.append({"id": f"{seed}-{i:05d}", "a": a, "b": b, "mode": mode, "answer": a + b})
        return items

    for i in range(n):
        a, b = _draw_from_pools(rng, train_single, train_multi)
        # Deterministic instruction assignment: alternate, offset per index.
        mode = "trace" if (i % 2 == 0) else "direct"
        items.append({"id": f"{seed}-{i:05d}", "a": a, "b": b, "mode": mode, "answer": a + b})
    return items


def assert_disjoint_splits(train_items, eval_items):
    train_pairs = {(item["a"], item["b"]) for item in train_items}
    eval_pairs = {(item["a"], item["b"]) for item in eval_items}
    assert not (train_pairs & eval_pairs), "train and eval operand pairs overlap"
    return train_pairs, eval_pairs


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
        base = make_items(
            TRAIN_ITEMS if split == "train" else EVAL_ITEMS,
            TRAIN_SEED if split == "train" else EVAL_SEED,
            split=split,
        )
        if split == "train" and _train_items_override > 0:
            k = _train_items_override // TRAIN_ITEMS
            base = base * k
            print(f"[suppression-arith] mixture duplicated x{k}: {len(base)} rows")
        self.items = base

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
    train_items = make_items(TRAIN_ITEMS, TRAIN_SEED, split="train")
    items = make_items(EVAL_ITEMS, EVAL_SEED, split="eval")
    assert_disjoint_splits(train_items, items)
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
