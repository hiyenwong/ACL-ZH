#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--experiment",required=True)
    ap.add_argument("--bundle",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    exp=json.loads(Path(args.experiment).read_text(encoding='utf-8'))
    bundle=Path(args.bundle)
    run_manifest=json.loads((bundle/'run-manifest.json').read_text(encoding='utf-8'))
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    results=out/'results.jsonl'
    if results.exists(): results.unlink()

    missing=[]
    for item in run_manifest:
        response=bundle/item['response']
        if not response.exists() or not response.read_text(encoding='utf-8').strip():
            missing.append(str(item['response']))
    if missing:
        print(json.dumps({'status':'INCOMPLETE','missing':missing},ensure_ascii=False,indent=2))
        raise SystemExit(2)

    scorer=Path(__file__).with_name('score_web_patch.py')
    for item in run_manifest:
        response=bundle/item['response']
        cmd=[
            sys.executable,str(scorer),
            '--manifest',args.manifest,
            '--task-id',item['task_id'],
            '--variant',item['variant'],
            '--provider',exp['provider'],
            '--model',exp['model'],
            '--response',str(response),
            '--output',str(results)
        ]
        subprocess.run(cmd,check=True)

    rows=[json.loads(x) for x in results.read_text(encoding='utf-8').splitlines() if x.strip()]
    summary={}
    for variant in exp['variants']:
        rs=[r for r in rows if r['variant']==variant]
        summary[variant]={
            'n':len(rs),
            'task_success_rate':sum(bool(r['task_success']) for r in rs)/len(rs),
            'hidden_oracle_pass_rate':sum(bool(r['hidden_oracle_pass']) for r in rs)/len(rs),
            'constraint_violation_rate':sum(bool(r['constraint_violation']) for r in rs)/len(rs),
            'patch_apply_rate':sum(r['patch_apply_exit_code']==0 for r in rs)/len(rs)
        }
    report={'experiment_id':exp['experiment_id'],'provider':exp['provider'],'model':exp['model'],'runs':len(rows),'summary':summary}
    (out/'aggregate.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
