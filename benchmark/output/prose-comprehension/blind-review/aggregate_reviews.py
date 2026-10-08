#!/usr/bin/env python3
import json, sys
from collections import defaultdict
from pathlib import Path

rows=[]
for path in sys.argv[1:]:
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
if not rows:
    raise SystemExit("no review rows")

groups=defaultdict(list)
for r in rows:
    groups[(r["item_id"],r["label"])].append(r)

summary=[]
for (item,label),rs in sorted(groups.items()):
    n=len(rs)
    eq=sum(bool(r["overall_equivalent"]) for r in rs)
    material=sum(
        r["extra_information"]=="material"
        or r["semantic_drift"]=="material"
        or r["terminology_drift"]=="material"
        or r["answer_leakage"]=="material"
        or r["fact_coverage"]=="fail"
        for r in rs
    )
    summary.append({
        "item_id":item,
        "label":label,
        "reviewers":n,
        "equivalence_rate":round(eq/n,4),
        "material_issue_rate":round(material/n,4),
        "consensus_equivalent": eq==n and material==0
    })

all_consensus=all(x["consensus_equivalent"] for x in summary)
print(json.dumps({
    "rows":len(rows),
    "reviewers":len(set(r["reviewer_id"] for r in rows)),
    "cells":len(summary),
    "all_cells_consensus_equivalent":all_consensus,
    "summary":summary
},ensure_ascii=False,indent=2))
