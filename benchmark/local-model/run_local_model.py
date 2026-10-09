#!/usr/bin/env python3
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="Qwen/Qwen2.5-Coder-0.5B-Instruct")
    ap.add_argument("--experiment",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--workdir",required=True)
    ap.add_argument("--max-new-tokens",type=int,default=512)
    ap.add_argument("--variant",default=None)
    args=ap.parse_args()

    exp=json.loads(Path(args.experiment).read_text(encoding='utf-8'))
    root=Path(args.workdir)
    root.mkdir(parents=True,exist_ok=True)

    exporter=Path(__file__).resolve().parents[1]/'web-eval'/'export_web_prompts.py'
    selected_variants=[args.variant] if args.variant else exp['variants']
    for variant in selected_variants:
        subprocess.run([sys.executable,str(exporter),'--manifest',args.manifest,'--variant',variant,'--output',str(root/variant)],check=True)

    run_manifest=[]
    responses=root/'responses'
    responses.mkdir(exist_ok=True)
    selected_entries=[x for x in exp['run_order'] if (not args.variant or x.endswith(':'+args.variant))]
    for i,entry in enumerate(selected_entries,1):
        task,variant=entry.split(':',1)
        run_manifest.append({'run':i,'task_id':task,'variant':variant,'prompt':f'{variant}/{task}-{variant}.md','response':f'responses/{i:02d}-{task}-{variant}.diff'})
    (root/'run-manifest.json').write_text(json.dumps(run_manifest,ensure_ascii=False,indent=2),encoding='utf-8')

    tokenizer=AutoTokenizer.from_pretrained(args.model)
    model=AutoModelForCausalLM.from_pretrained(args.model,torch_dtype=torch.float32)
    model.eval()

    metadata=[]
    for item in run_manifest:
        prompt=(root/item['prompt']).read_text(encoding='utf-8')
        messages=[{'role':'user','content':prompt}]
        text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        inputs=tokenizer([text],return_tensors='pt')
        with torch.no_grad():
            out=model.generate(**inputs,max_new_tokens=args.max_new_tokens,do_sample=False)
        generated=out[0][inputs.input_ids.shape[1]:]
        response=tokenizer.decode(generated,skip_special_tokens=True)
        (root/item['response']).write_text(response,encoding='utf-8')
        metadata.append({'run':item['run'],'task_id':item['task_id'],'variant':item['variant'],'response_chars':len(response)})
        print(json.dumps(metadata[-1],ensure_ascii=False),flush=True)

    (root/'generation-metadata.json').write_text(json.dumps({
        'model':args.model,
        'torch_version':torch.__version__,
        'max_new_tokens':args.max_new_tokens,
        'do_sample':False,
        'runs':metadata
    },ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=="__main__":
    main()
