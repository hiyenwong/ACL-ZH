#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    root = Path(args.workdir)
    exp = load_json(args.experiment)
    runs = load_json(root / "run-manifest.json")
    meta = load_json(root / "generation-metadata.json")
    model = meta["model"]

    strict = root / "results-strict.jsonl"
    normalized = root / "results-normalized.jsonl"
    strict.unlink(missing_ok=True)
    normalized.unlink(missing_ok=True)

    score = Path(__file__).resolve().parents[1] / "web-eval" / "score_web_patch.py"
    normalize = Path(__file__).resolve().parent / "normalize_diff_fence.py"
    norm_root = root / "responses-normalized"
    norm_root.mkdir(exist_ok=True)

    for item in runs:
        raw = root / item["response"]
        subprocess.run([
            sys.executable, str(score),
            "--manifest", args.manifest,
            "--task-id", item["task_id"],
            "--variant", item["variant"],
            "--provider", "lm-studio-local",
            "--model", model,
            "--track", "local-lm-studio",
            "--agent", "openai-compatible-chat-completions",
            "--response", str(raw),
            "--output", str(strict),
        ], check=True)

        norm = norm_root / raw.name
        subprocess.run([
            sys.executable, str(normalize),
            "--input", str(raw),
            "--output", str(norm),
        ], check=True)
        subprocess.run([
            sys.executable, str(score),
            "--manifest", args.manifest,
            "--task-id", item["task_id"],
            "--variant", item["variant"],
            "--provider", "lm-studio-local",
            "--model", model,
            "--track", "local-lm-studio-normalized",
            "--agent", "openai-compatible-chat-completions",
            "--response", str(norm),
            "--output", str(normalized),
        ], check=True)

    s = [json.loads(x) for x in strict.read_text(encoding="utf-8").splitlines() if x.strip()]
    n = [json.loads(x) for x in normalized.read_text(encoding="utf-8").splitlines() if x.strip()]
    summary = {}
    for variant in exp["variants"]:
        ss = [r for r in s if r["variant"] == variant]
        nn = [r for r in n if r["variant"] == variant]
        summary[variant] = {
            "n": len(ss),
            "strict_patch_apply": sum(r["patch_apply_exit_code"] == 0 for r in ss),
            "strict_hidden_oracle_pass": sum(bool(r["hidden_oracle_pass"]) for r in ss),
            "strict_task_success": sum(bool(r["task_success"]) for r in ss),
            "normalized_patch_apply": sum(r["patch_apply_exit_code"] == 0 for r in nn),
            "normalized_hidden_oracle_pass": sum(bool(r["hidden_oracle_pass"]) for r in nn),
            "normalized_task_success": sum(bool(r["task_success"]) for r in nn),
        }

    matrix = {}
    for r in n:
        matrix.setdefault(r["task_id"], {})[r["variant"]] = bool(r["task_success"])

    out = {
        "experiment_id": exp["experiment_id"],
        "provider": "lm-studio-local",
        "model": model,
        "runs": len(s),
        "summary": summary,
        "normalized_task_matrix": matrix,
    }
    (root / "aggregate.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
