#!/usr/bin/env python3
import json, sys
from pathlib import Path

REQUIRED_VARIANTS=["natural","light_acl","full_acl"]

def tokens(s):
    return {x for x in s.replace("。"," ").replace("，"," ").replace("；"," ").replace("："," ").split() if x}

errors=[]
items=[]
for line_no,line in enumerate(Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(),1):
    if not line.strip():
        continue
    try:
        item=json.loads(line)
    except Exception as e:
        errors.append(f"line {line_no}: invalid JSON: {e}")
        continue
    items.append(item)
    for key in ["id","domain","fact_sheet","questions",*REQUIRED_VARIANTS]:
        if key not in item:
            errors.append(f"{item.get('id',line_no)}: missing {key}")
    if len(item.get("fact_sheet",[])) < 3:
        errors.append(f"{item.get('id')}: fact_sheet too small")
    if len(item.get("questions",[])) < 2:
        errors.append(f"{item.get('id')}: fewer than 2 questions")
    for variant in REQUIRED_VARIANTS:
        if not item.get(variant):
            errors.append(f"{item.get('id')}: empty {variant}")

ids=[x["id"] for x in items if "id" in x]
if len(ids)!=len(set(ids)):
    errors.append("duplicate item ids")

print(json.dumps({
    "items":len(items),
    "domains":sorted(set(x.get("domain") for x in items)),
    "errors":errors,
    "status":"PASS" if not errors else "FAIL"
},ensure_ascii=False,indent=2))

raise SystemExit(1 if errors else 0)
