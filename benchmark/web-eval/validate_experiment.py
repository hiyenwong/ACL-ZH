#!/usr/bin/env python3
import json, sys
from pathlib import Path

p=Path(sys.argv[1])
e=json.loads(p.read_text(encoding='utf-8'))
errors=[]
tasks=e['tasks']
variants=e['variants']
expected={f'{t}:{v}' for t in tasks for v in variants}
actual=e['run_order']
if len(actual)!=len(expected):
    errors.append(f'expected {len(expected)} runs, got {len(actual)}')
if set(actual)!=expected:
    missing=sorted(expected-set(actual))
    extra=sorted(set(actual)-expected)
    if missing: errors.append(f'missing: {missing}')
    if extra: errors.append(f'extra: {extra}')
if len(actual)!=len(set(actual)):
    errors.append('duplicate run entries')
if e.get('repetitions')!=1:
    errors.append('smoke v0.1 must use one repetition')
if e.get('track') == 'web-manual' and not e.get('fresh_chat_per_run'):
    errors.append('fresh_chat_per_run must be true for web-manual experiments')
print(json.dumps({'experiment_id':e.get('experiment_id'),'runs':len(actual),'status':'PASS' if not errors else 'FAIL','errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
