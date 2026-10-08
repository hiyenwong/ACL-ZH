#!/usr/bin/env python3
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

rows = []
for arg in sys.argv[1:]:
    for line in Path(arg).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))

if not rows:
    raise SystemExit("no result rows")

groups = defaultdict(list)
for r in rows:
    key = (
        r.get("agent"),
        r.get("model"),
        r.get("reasoning_effort"),
        r.get("cli_version"),
        r.get("variant"),
    )
    groups[key].append(r)


def rate(rs, key):
    return sum(bool(r.get(key)) for r in rs) / len(rs)


summary = []
for (agent, model, reasoning, cli_version, variant), rs in sorted(
    groups.items(), key=lambda x: tuple("" if v is None else str(v) for v in x[0])
):
    elapsed = [r["elapsed_seconds"] for r in rs]
    changed_counts = [len(r.get("changed_files", [])) for r in rs]
    summary.append(
        {
            "agent": agent,
            "model": model,
            "reasoning_effort": reasoning,
            "cli_version": cli_version,
            "variant": variant,
            "n": len(rs),
            "task_success_rate": round(rate(rs, "task_success"), 4),
            "first_pass_success_rate": round(rate(rs, "first_pass_success"), 4),
            "visible_tests_pass_rate": round(rate(rs, "visible_tests_pass"), 4),
            "hidden_oracle_pass_rate": round(rate(rs, "hidden_oracle_pass"), 4),
            "constraint_violation_rate": round(rate(rs, "constraint_violation"), 4),
            "wrong_file_modification_rate": round(
                sum(bool(r.get("forbidden_path_changes")) for r in rs) / len(rs), 4
            ),
            "unrequested_change_rate": round(
                sum(bool(r.get("unrequested_changes")) for r in rs) / len(rs), 4
            ),
            "agent_exit_success_rate": round(
                sum(r.get("agent_exit_code") == 0 for r in rs) / len(rs), 4
            ),
            "mean_changed_files": round(statistics.mean(changed_counts), 3),
            "mean_elapsed_seconds": round(statistics.mean(elapsed), 3),
            "median_elapsed_seconds": round(statistics.median(elapsed), 3),
        }
    )

print(json.dumps({"runs": len(rows), "summary": summary}, ensure_ascii=False, indent=2))
