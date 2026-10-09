#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, subprocess, tempfile, time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT=Path(__file__).resolve().parents[2]
RUNNER=ROOT/"benchmark"/"agent-eval"/"run.py"
spec=importlib.util.spec_from_file_location("aclzh_runner",RUNNER)
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

BLOCK_RE=re.compile(r'<<<([^>\\n]+)>>>(?:\\s*\\n)?```(?:python)?\\s*\\n(.*?)```',re.S|re.I)

def load_manifest(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]

def build_prompt(task,variant,files):
    chunks=['You are editing a small Python workspace.','', '## Instruction', task[variant], '', '## Workspace files']
    for path,content in files.items():
        chunks += ['',f'### {path}','```python',content.rstrip(),'```']
    chunks += ['', '## Response contract',
      'For every file you change, return exactly one block in this form:',
      '<<<path/to/file>>>',
      '```python',
      '<complete final file content>',
      '```',
      'Return only changed-file blocks. Do not use unified diff. Do not invent file paths.']
    return '\n'.join(chunks)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--variant",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--max-new-tokens",type=int,default=384)
    args=ap.parse_args()
    tasks=load_manifest(args.manifest)
    tokenizer=AutoTokenizer.from_pretrained(args.model)
    model=AutoModelForCausalLM.from_pretrained(args.model,torch_dtype=torch.float32)
    model.eval()
    outdir=Path(args.output); outdir.mkdir(parents=True,exist_ok=True)
    rawdir=outdir/'raw'; rawdir.mkdir(exist_ok=True)
    outfile=outdir/'results.jsonl'
    if outfile.exists(): outfile.unlink()

    for task in tasks:
      with tempfile.TemporaryDirectory(prefix='aclzh-controlled-v02-') as td:
        ws=Path(td); runner.write_fixture(ws)
        runner.sh('git init -q && git config user.email benchmark@example.invalid && git config user.name benchmark && git add . && git commit -qm baseline',ws)
        allowed=set(task.get('allowed_paths',[])); forbidden=set(task.get('forbidden_paths',[]))
        relevant=sorted(allowed|forbidden)
        files={p:(ws/p).read_text(encoding='utf-8') for p in relevant if (ws/p).exists()}
        prompt=build_prompt(task,args.variant,files)
        formatted=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        inputs=tokenizer([formatted],return_tensors='pt')
        start=time.time()
        with torch.no_grad(): generated=model.generate(**inputs,max_new_tokens=args.max_new_tokens,do_sample=False)
        elapsed=time.time()-start
        response=tokenizer.decode(generated[0][inputs.input_ids.shape[1]:],skip_special_tokens=True)
        (rawdir/f"{task['id']}-{args.variant}.txt").write_text(response,encoding='utf-8')

        blocks=file_block_parser.extract_blocks(response)
        protocol=[]; applied=[]
        for path,content in blocks:
          if path not in allowed:
            protocol.append(path); continue
          target=ws/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(content,encoding='utf-8'); applied.append(path)
        changed=runner.git_changed(ws)
        tests=runner.sh(task['test_command'],ws,timeout=120)
        oracle_ok=runner.hidden_oracle(task['id'],ws)
        forbidden_changed=[p for p in forbidden if p in changed]
        unrequested=[p for p in changed if p not in allowed]
        constraint_violation=bool(protocol or forbidden_changed or unrequested)
        success=tests.returncode==0 and oracle_ok and not constraint_violation
        stripped=file_block_parser.BLOCK_RE.sub('',response).strip()
        format_compliant=bool(blocks) and not stripped and not protocol
        row={
          'task_id':task['id'],'category':task['category'],'track':'controlled-v0.2-local-open-model',
          'variant':args.variant,'agent':'local-causal-lm','provider':'huggingface-hub-local','model':args.model,
          'response_sha256':hashlib.sha256(response.encode()).hexdigest(),'elapsed_seconds':round(elapsed,3),
          'parsed_file_count':len(blocks),'parsed_paths':[p for p,_ in blocks],'applied_paths':applied,
          'format_compliant':format_compliant,'changed_files':changed,
          'forbidden_path_changes':forbidden_changed,'unrequested_changes':unrequested,'protocol_violations':protocol,
          'visible_tests_pass':tests.returncode==0,'hidden_oracle_pass':oracle_ok,
          'constraint_violation':constraint_violation,'task_success':success,
          'test_stdout':tests.stdout[-12000:],'test_stderr':tests.stderr[-12000:]
        }
        with outfile.open('a',encoding='utf-8') as f: f.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(json.dumps({k:row[k] for k in ['task_id','variant','parsed_file_count','format_compliant','hidden_oracle_pass','task_success']},ensure_ascii=False),flush=True)

if __name__=="__main__": main()
