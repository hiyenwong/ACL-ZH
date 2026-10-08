#!/usr/bin/env python3
import argparse, json, random
from pathlib import Path

VARIANTS=["natural","light_acl","full_acl"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--out-dir", required=True)
    args=ap.parse_args()

    out=Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    review_path=out/"review-pack.jsonl"
    key_path=out/"answer-key.jsonl"

    rng=random.Random(args.seed)

    reviews=[]
    keys=[]
    for line in Path(args.items).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item=json.loads(line)
        order=VARIANTS[:]
        rng.shuffle(order)
        labels=["A","B","C"]
        mapping=dict(zip(labels,order))

        reviews.append({
            "item_id":item["id"],
            "domain":item["domain"],
            "difficulty":item.get("difficulty"),
            "fact_sheet":item["fact_sheet"],
            "versions":[
                {"label":label,"text":item[mapping[label]]}
                for label in labels
            ]
        })
        keys.append({
            "item_id":item["id"],
            "seed":args.seed,
            "mapping":mapping
        })

    review_path.write_text(
        "\n".join(json.dumps(x,ensure_ascii=False) for x in reviews)+"\n",
        encoding="utf-8"
    )
    key_path.write_text(
        "\n".join(json.dumps(x,ensure_ascii=False) for x in keys)+"\n",
        encoding="utf-8"
    )
    print(json.dumps({
        "items":len(reviews),
        "review_pack":str(review_path),
        "answer_key":str(key_path)
    },ensure_ascii=False))

if __name__=="__main__":
    main()
