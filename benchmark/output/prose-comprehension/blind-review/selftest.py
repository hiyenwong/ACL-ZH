#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

items=sys.argv[1]
script=Path(__file__).with_name("anonymize.py")

with tempfile.TemporaryDirectory() as td:
    subprocess.run(
        [sys.executable,str(script),"--items",items,"--seed","20261008","--out-dir",td],
        check=True,capture_output=True,text=True
    )
    review=[json.loads(x) for x in (Path(td)/"review-pack.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    key=[json.loads(x) for x in (Path(td)/"answer-key.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(review)==10
    assert len(key)==10
    assert all(set(v["label"] for v in x["versions"])=={"A","B","C"} for x in review)
    serialized="\n".join(json.dumps(x,ensure_ascii=False) for x in review)
    for forbidden in ["natural","light_acl","full_acl"]:
        assert forbidden not in serialized
    maps=[tuple(sorted(x["mapping"].items())) for x in key]
    assert len(set(maps)) > 1, "all items received identical mapping; blinding is weak"
    print(json.dumps({"status":"PASS","items":len(review),"unique_mappings":len(set(maps))},ensure_ascii=False))
