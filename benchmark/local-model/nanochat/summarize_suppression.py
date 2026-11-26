#!/usr/bin/env python3
"""Turn the two nanochat arm evaluations into the preregistered report table.

Reads eval-<arm>.summary.json files written by eval_suppression.py and applies
the gates frozen in PREREG-NANOCHAT-SUPPRESSION-V0.1.md.
"""
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace-summary", required=True)
    ap.add_argument("--direct-summary", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    arms = {"trace-trained": load(args.trace_summary), "direct-trained": load(args.direct_summary)}

    lines = ["| Arm | Instruction | Accuracy | Mean visible chars | Leak rate (visible work > 0) | Step pattern rate | Mean generated tokens |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for arm, s in arms.items():
        for mode in ("direct", "trace"):
            m = s["by_mode"][mode]
            lines.append(
                f"| {arm} | {mode} | {m['accuracy']:.3f} | {m['mean_prefix_chars']:.1f} | "
                f"{m['leak_rate_prefix_chars_gt_0']:.3f} | {m['step_pattern_rate']:.3f} | "
                f"{m['mean_generated_tokens']:.1f} |"
            )

    single = {arm: s["by_mode_and_size"]["direct_single"]["accuracy"] for arm, s in arms.items()}
    multi = {arm: s["by_mode_and_size"]["direct_multi"]["accuracy"] for arm, s in arms.items()}
    direct_acc = {arm: s["by_mode"]["direct"]["accuracy"] for arm, s in arms.items()}

    floor = all(v < 0.50 for v in single.values())
    ceiling = all(v >= 0.98 for v in direct_acc.values())

    report = {
        "arms": {arm: {"overall": s["overall"], "by_mode": s["by_mode"],
                       "by_mode_and_size": s["by_mode_and_size"],
                       "model_tag": s["model_tag"]} for arm, s in arms.items()},
        "gates": {
            "single_digit_direct_accuracy": single,
            "multi_digit_direct_accuracy": multi,
            "learnability_floor": floor,
            "ceiling": ceiling,
            "interpretation": (
                "capability floor: no arm-difference claim (escalate to --depth=12)"
                if floor else
                "saturated: suppression endpoints are ceiling-limited"
                if ceiling else
                "task is inside the discriminating band"
            ),
        },
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(lines))
    print()
    print(json.dumps(report["gates"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
