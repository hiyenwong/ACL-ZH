#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--allow-version-mismatch", action="store_true",
                    help="Score even when actual scoring-input hashes differ from "
                         "the generation-time baseline; the mismatch is recorded "
                         "and the score labeled a rescore. Default: fail closed.")
    args = ap.parse_args()

    root = Path(args.workdir)
    exp = load_json(args.experiment)
    runs = load_json(root / "run-manifest.json")
    meta = load_json(root / "generation-metadata.json")
    model = meta["model"]

    score = Path(__file__).resolve().parents[1] / "web-eval" / "score_web_patch.py"
    normalize = Path(__file__).resolve().parent / "normalize_diff_fence.py"
    oracle_runner = Path(__file__).resolve().parents[1] / "agent-eval" / "run.py"

    actual_prov = provenance.scoring_provenance(
        workdir=root, run_manifest=runs,
        manifest=args.manifest, experiment=args.experiment,
        extra={
            "scorer_sha256": provenance.sha256_file(__file__),
            "patch_scorer_sha256": provenance.sha256_file(score),
            "normalizer_sha256": provenance.sha256_file(normalize),
            "oracle_sha256": provenance.sha256_file(oracle_runner),
            "parser_sha256": None,  # strict-diff track has no content parser
        },
    )
    recorded_prov = meta.get("provenance") or {}
    status, mismatches, missing = provenance.verify_provenance(recorded_prov, actual_prov)
    if status == "mismatch" and not args.allow_version_mismatch:
        raise SystemExit(
            "Provenance mismatch between generation-time baseline and the actual "
            "scoring inputs (fail-closed). Re-run with --allow-version-mismatch to "
            "score anyway; the mismatch will be recorded and labeled a rescore.\n"
            + json.dumps(mismatches, indent=2)
        )
    prov_block = {
        "status": "mismatch_overridden" if status == "mismatch" else status,
        "score_kind": "initial" if status == "verified" else "rescore",
        "actual": actual_prov,
        "recorded": {k: recorded_prov.get(k) for k in provenance.COMPARE_KEYS},
        "mismatches": mismatches,
        "missing_baseline": missing,
    }

    strict = root / "results-strict.jsonl"
    normalized = root / "results-normalized.jsonl"
    strict.unlink(missing_ok=True)
    normalized.unlink(missing_ok=True)

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
        "provenance": prov_block,
    }
    (root / "aggregate.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
