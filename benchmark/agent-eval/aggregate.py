#!/usr/bin/env python3
import json, statistics, sys
from collections import defaultdict
from pathlib import Path

rows=[]
for arg in sys.argv[1:]:
    for line in Path(arg).read_text(encoding="utf-8").splitlines():
        if line.strip(): rows.append(json.loads(line))
if not rows:
    raise SystemExit("no result rows")

groups=defaultdict(list)
for r in rows:
    groups[(r["agent"],r["variant"])].append(r)

def rate(rs,key):
    return sum(bool(r.get(key)) for r in rs)/len(rs)

summary=[]
for (agent,variant),rs in sorted(groups.items()):
    elapsed=[r["elapsed_seconds"] for r in rs]
    summary.append({
      "agent":agent,"variant":variant,"n":len(rs),
      "task_success_rate":round(rate(rs,"task_success"),4),
      "tests_pass_rate":round(rate(rs,"tests_pass"),4),
      "constraint_violation_rate":round(rate(rs,"constraint_violation"),4),
      "unrequested_change_rate":round(sum(bool(r.get("unrequested_changes")) for r in rs)/len(rs),4),
      "mean_elapsed_seconds":round(statistics.mean(elapsed),3),
      "median_elapsed_seconds":round(statistics.median(elapsed),3),
    })

print(json.dumps({"runs":len(rows),"summary":summary},ensure_ascii=False,indent=2))
