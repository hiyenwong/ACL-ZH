#!/usr/bin/env python3
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

rows=[]
for path in sys.argv[1:]:
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))

if not rows:
    raise SystemExit("no response rows")

groups=defaultdict(list)
for r in rows:
    groups[r["variant"]].append(r)

summary=[]
for variant, rs in sorted(groups.items()):
    times=[r["response_time_ms"] for r in rs if r.get("response_time_ms") is not None]
    loads=[r["cognitive_load"] for r in rs if r.get("cognitive_load") is not None]
    recall=[r["delayed_recall_correct"] for r in rs if r.get("delayed_recall_correct") is not None]
    correct=sum(bool(r["correct"]) for r in rs)
    participants=len(set(r["participant_id"] for r in rs))
    summary.append({
        "variant": variant,
        "participants": participants,
        "responses": len(rs),
        "comprehension_accuracy": round(correct/len(rs),4),
        "misinterpretation_rate": round(1-correct/len(rs),4),
        "median_response_time_ms": round(statistics.median(times),2) if times else None,
        "mean_response_time_ms": round(statistics.mean(times),2) if times else None,
        "mean_cognitive_load": round(statistics.mean(loads),3) if loads else None,
        "delayed_recall_accuracy": round(sum(bool(x) for x in recall)/len(recall),4) if recall else None,
        "understanding_efficiency_exploratory": round(correct/(sum(times)/1000),4) if times and sum(times)>0 else None
    })

print(json.dumps({
    "note":"Understanding efficiency is exploratory and is not a validated psychometric construct.",
    "summary":summary
},ensure_ascii=False,indent=2))
