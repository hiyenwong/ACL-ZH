#!/usr/bin/env python3
import json, sys
from collections import Counter
from pathlib import Path

rows=[]
for p in sys.argv[1:]:
    for line in Path(p).read_text(encoding='utf-8').splitlines():
        if line.strip(): rows.append(json.loads(line))
errors=[]
required={'reviewer_id','item_id','label','fact_coverage','extra_information','semantic_drift','terminology_drift','answer_leakage','overall_equivalent'}
for i,r in enumerate(rows,1):
    missing=required-set(r)
    if missing: errors.append(f'row {i}: missing {sorted(missing)}')
    if r.get('label') not in {'A','B','C'}: errors.append(f'row {i}: invalid label')
reviewers=sorted(set(r.get('reviewer_id') for r in rows if r.get('reviewer_id')))
for reviewer in reviewers:
    rr=[r for r in rows if r.get('reviewer_id')==reviewer]
    cells=Counter((r.get('item_id'),r.get('label')) for r in rr)
    if len(rr)!=30: errors.append(f'{reviewer}: expected 30 rows, got {len(rr)}')
    dup=[k for k,v in cells.items() if v!=1]
    if dup: errors.append(f'{reviewer}: duplicate/missing cells {dup[:5]}')
print(json.dumps({'reviewers':reviewers,'rows':len(rows),'status':'PASS' if not errors else 'FAIL','errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
