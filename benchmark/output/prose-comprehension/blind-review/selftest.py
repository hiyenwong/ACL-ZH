#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

items=sys.argv[1]
base=Path(__file__).parent
anonymize=base/'anonymize.py'
builder=base/'build_reviewer_html.py'
validator=base/'validate_reviews.py'

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    subprocess.run([sys.executable,str(anonymize),'--items',items,'--seed','20261008','--out-dir',str(td)],check=True,capture_output=True,text=True)
    review=[json.loads(x) for x in (td/'review-pack.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    key=json.loads((td/'answer-key.json').read_text(encoding='utf-8'))
    assert len(review)==10
    assert len(key['items'])==10
    assert all(set(v['label'] for v in x['versions'])=={'A','B','C'} for x in review)
    serialized='\n'.join(json.dumps(x,ensure_ascii=False) for x in review)
    for forbidden in ['natural','light_acl','full_acl']:
        assert forbidden not in serialized
    maps=[tuple(sorted(x['mapping'].items())) for x in key['items']]
    assert len(set(maps))>1, 'all items received identical mapping; blinding is weak'

    html_path=td/'reviewer.html'
    subprocess.run([sys.executable,str(builder),'--review-pack',str(td/'review-pack.jsonl'),'--output',str(html_path)],check=True,capture_output=True,text=True)
    html=html_path.read_text(encoding='utf-8')
    assert 'ACL-ZH Independent Blind Review' in html
    for forbidden in ['natural','light_acl','full_acl']:
        assert forbidden not in html

    rows=[]
    for item in review:
        for version in item['versions']:
            rows.append({
                'reviewer_id':'selftest-reviewer',
                'item_id':item['item_id'],
                'label':version['label'],
                'fact_coverage':'pass',
                'extra_information':'none',
                'semantic_drift':'none',
                'terminology_drift':'none',
                'answer_leakage':'none',
                'overall_equivalent':True,
                'notes':None
            })
    response_path=td/'selftest-review.jsonl'
    response_path.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,str(validator),str(response_path)],check=True,capture_output=True,text=True)

    print(json.dumps({'status':'PASS','items':len(review),'cells':len(rows),'unique_mappings':len(set(maps))},ensure_ascii=False))
