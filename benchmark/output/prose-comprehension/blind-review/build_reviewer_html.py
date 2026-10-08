#!/usr/bin/env python3
import argparse, json
from pathlib import Path

HTML_HEAD='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ACL-ZH Blind Review</title><style>body{font-family:system-ui,-apple-system,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;line-height:1.55}.card{border:1px solid #bbb;border-radius:12px;padding:18px;margin:18px 0}.version{background:#f6f6f6;padding:14px;border-radius:8px;white-space:pre-wrap}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}label{display:block;font-weight:600}select,input,textarea{width:100%;box-sizing:border-box;padding:8px;margin-top:4px}button{padding:10px 16px;margin:10px 8px 10px 0}.notice{background:#fff8d8;padding:12px;border-radius:8px}</style></head><body><h1>ACL-ZH Independent Blind Review</h1><div class="notice">只比较文本与 Fact Sheet 是否信息等价。不要评价文风、可读性、喜好，也不要猜测 A/B/C 对应哪一种写法。</div><label>Reviewer ID<input id="reviewer" placeholder="reviewer-01"></label><div id="root"></div><button onclick="downloadRows()">导出 review JSONL</button><script>'''
HTML_TAIL='''</script></body></html>'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--review-pack',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    items=[json.loads(x) for x in Path(args.review_pack).read_text(encoding='utf-8').splitlines() if x.strip()]
    payload=json.dumps(items,ensure_ascii=False).replace('</','<\\/')
    js=r'''
const items=__PAYLOAD__;
const enums={fact_coverage:['pass','minor','fail'],extra_information:['none','minor','material'],semantic_drift:['none','minor','material'],terminology_drift:['none','minor','material'],answer_leakage:['none','low','material']};
function makeSelect(key,id){let s='<select data-k="'+key+'" data-id="'+id+'">';for(const x of enums[key])s+='<option value="'+x+'">'+x+'</option>';return s+'</select>';}
const root=document.getElementById('root');
for(const item of items){const facts='<ul>'+item.fact_sheet.map(x=>'<li>'+x+'</li>').join('')+'</ul>';for(const v of item.versions){const id=item.item_id+'::'+v.label;let h='<div class="card"><h2>'+item.item_id+' / Version '+v.label+'</h2><h3>Fact Sheet</h3>'+facts+'<h3>匿名文本</h3><div class="version">'+v.text+'</div><div class="grid">';for(const k of Object.keys(enums))h+='<label>'+k+makeSelect(k,id)+'</label>';h+='<label>overall_equivalent<select data-k="overall_equivalent" data-id="'+id+'"><option value="true">true</option><option value="false">false</option></select></label></div><label>notes<textarea data-k="notes" data-id="'+id+'" rows="3"></textarea></label></div>';root.insertAdjacentHTML('beforeend',h);}}
function downloadRows(){const reviewer=document.getElementById('reviewer').value.trim();if(!reviewer){alert('请填写 Reviewer ID');return;}const rows=[];for(const item of items){for(const v of item.versions){const id=item.item_id+'::'+v.label;const row={reviewer_id:reviewer,item_id:item.item_id,label:v.label};document.querySelectorAll('[data-id="'+id+'"]').forEach(el=>{let val=el.value;if(el.dataset.k==='overall_equivalent')val=(val==='true');row[el.dataset.k]=val||null;});rows.push(row);}}const blob=new Blob([rows.map(x=>JSON.stringify(x)).join('\n')+'\n'],{type:'application/x-ndjson'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=reviewer+'-blind-review.jsonl';a.click();URL.revokeObjectURL(a.href);}
'''.replace('__PAYLOAD__',payload)
    Path(args.output).write_text(HTML_HEAD+js+HTML_TAIL,encoding='utf-8')
    print(json.dumps({'items':len(items),'cells':len(items)*3,'output':args.output},ensure_ascii=False))

if __name__=='__main__':
    main()
