#!/usr/bin/env python3
import argparse
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def http_json(url, payload=None, token=None, timeout=600):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=20261011)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--api-token", default=os.environ.get("LM_STUDIO_API_TOKEN"))
    args = ap.parse_args()

    exp = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    root = Path(args.workdir)
    root.mkdir(parents=True, exist_ok=True)

    exporter = Path(__file__).resolve().parents[1] / "web-eval" / "export_web_prompts.py"
    for variant in exp["variants"]:
        subprocess.run(
            [sys.executable, str(exporter), "--manifest", args.manifest,
             "--variant", variant, "--output", str(root / variant)],
            check=True,
        )

    run_manifest = []
    responses = root / "responses"
    responses.mkdir(exist_ok=True)
    for i, entry in enumerate(exp["run_order"], 1):
        task, variant = entry.split(":", 1)
        run_manifest.append({
            "run": i,
            "task_id": task,
            "variant": variant,
            "prompt": f"{variant}/{task}-{variant}.md",
            "response": f"responses/{i:02d}-{task}-{variant}.diff",
        })
    (root / "run-manifest.json").write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Verify that the requested model is visible before starting scored runs.
    models = http_json(args.base_url.rstrip("/") + "/models", token=args.api_token, timeout=args.timeout)
    model_ids = [m.get("id") for m in models.get("data", [])]
    if args.model not in model_ids:
        raise SystemExit(
            f"Model {args.model!r} not found at LM Studio endpoint. Available: {model_ids}"
        )

    metadata = []
    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    for item in run_manifest:
        prompt = (root / item["prompt"]).read_text(encoding="utf-8")
        payload = {
            "model": args.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": args.temperature,
            "top_p": args.top_p,
            "seed": args.seed,
            "max_tokens": args.max_tokens,
            "stream": False,
        }
        started = time.time()
        result = http_json(endpoint, payload=payload, token=args.api_token, timeout=args.timeout)
        elapsed = time.time() - started
        try:
            response = result["choices"][0]["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Unexpected LM Studio response: {result}") from exc
        if response is None:
            response = ""
        (root / item["response"]).write_text(response, encoding="utf-8")
        row = {
            "run": item["run"],
            "task_id": item["task_id"],
            "variant": item["variant"],
            "response_chars": len(response),
            "elapsed_seconds": round(elapsed, 3),
            "usage": result.get("usage"),
        }
        metadata.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    env = {
        "runner": "lm-studio-openai-compatible",
        "base_url": args.base_url,
        "model": args.model,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "seed": args.seed,
        "max_tokens": args.max_tokens,
        "experiment": args.experiment,
        "manifest": args.manifest,
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "runs": metadata,
    }
    (root / "generation-metadata.json").write_text(
        json.dumps(env, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
