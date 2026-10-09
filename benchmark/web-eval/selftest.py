#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

base=Path(__file__).parent
root=base.parents[1]
exporter=base/'export_web_prompts.py'
scorer=base/'score_web_patch.py'
manifest=root/'tasks'/'manifest.jsonl'

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    prompts=td/'prompts'
    subprocess.run([sys.executable,str(exporter),'--manifest',str(manifest),'--variant','baseline','--output',str(prompts)],check=True)
    index=json.loads((prompts/'index.json').read_text(encoding='utf-8'))
    assert len(index)==6, len(index)

    patch_lines=[
        'diff --git a/src/user_service.py b/src/user_service.py',
        '--- a/src/user_service.py',
        '+++ b/src/user_service.py',
        '@@ -1,2 +1,4 @@',
        ' def get_user(user_id):',
        "-    return {'id': user_id, 'name': '  Alice  '}",
        "+    user = {'id': user_id, 'name': '  Alice  '}",
        "+    user['name'] = user['name'].strip()",
        '+    return user',
    ]
    diff=td/'response.diff'
    diff.write_text('\n'.join(patch_lines)+'\n',encoding='utf-8')
    results=td/'results.jsonl'
    subprocess.run([sys.executable,str(scorer),'--manifest',str(manifest),'--task-id','scope-01','--variant','baseline','--provider','selftest','--model','reference-patch','--response',str(diff),'--output',str(results)],check=True)
    rows=[json.loads(x) for x in results.read_text(encoding='utf-8').splitlines() if x.strip()]
    assert len(rows)==1
    assert rows[0]['task_success'] is True, rows[0]
    assert rows[0]['track']=='web-manual'
    print('web-manual self-test: PASS')
