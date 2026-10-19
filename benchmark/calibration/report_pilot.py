#!/usr/bin/env python3
"""Fail-closed readiness report for the baseline-only calibration pilot."""
import argparse
import hashlib
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    root = Path(args.workdir)
    exp = json.loads(Path(args.experiment).read_text())
    tasks = [json.loads(line) for line in Path(args.manifest).read_text().splitlines() if line.strip()]
    meta = json.loads((root / "generation-metadata.json").read_text())
    agg = json.loads((root / "aggregate-edit-content.json").read_text())
    rows = [json.loads(line) for line in (root / "results-edit-content.jsonl").read_text().splitlines() if line.strip()]
    runs = json.loads((root / "run-manifest.json").read_text())
    expected = {t["id"] for t in tasks}
    ids = [r["task_id"] for r in rows]
    observations = meta.get("runs", [])
    errors = []
    if exp.get("variants") != ["baseline"]:
        errors.append("experiment must contain baseline only")
    if set(ids) != expected or len(ids) != len(expected):
        errors.append("incomplete or duplicated baseline results")
    if len(observations) != len(rows) or len(runs) != len(rows):
        errors.append("generation/results/run counts differ")
    if agg.get("provenance", {}).get("status") != "verified":
        errors.append("provenance is not verified")
    if meta.get("git_sha") is None or meta.get("provenance", {}).get("git_dirty") is not False:
        errors.append("generation requires known clean git commit")
    if meta.get("model") != exp.get("model"):
        errors.append("experiment model differs from generation model")
    dec = exp.get("decoding", {})
    for key in ("temperature", "top_p", "seed", "max_tokens", "reasoning_effort"):
        if dec.get(key) != meta.get(key):
            errors.append("decoding mismatch: " + key)
    truncated = sum(r.get("finish_reason") == "length" for r in observations)
    for r in rows:
        if r.get("track") != "local-lm-studio-edit-content" or r.get("variant") != "baseline":
            errors.append("cross-track or non-baseline result")
    success = sum(bool(r.get("task_success")) for r in rows)
    n = len(rows)
    valid = n - truncated
    rate = success / n if n else 0
    integrity = valid / n if n else 0
    if errors:
        decision = "INCONCLUSIVE"
    elif 0.2 <= rate <= 0.8 and integrity >= 0.95:
        decision = "GO"
    else:
        decision = "NO-GO"
    output = {
        "phase": "M2-01 baseline pilot", "decision": decision,
        "model": meta.get("model"), "n": n, "task_success": success,
        "success_rate": rate, "truncated": truncated, "nontruncated_rate": integrity,
        "format_compliant": sum(bool(r.get("format_compliant")) for r in rows),
        "semantic_success": sum(bool(r.get("semantic_task_success")) for r in rows),
        "contract_failures": sum(not r.get("format_compliant") for r in rows),
        "per_task": [{"id": r["task_id"], "success": bool(r.get("task_success")),
                      "format_compliant": bool(r.get("format_compliant")),
                      "semantic_success": bool(r.get("semantic_task_success"))} for r in rows],
        "provenance_status": agg.get("provenance", {}).get("status"),
        "manifest_sha256": hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest(),
        "experiment_sha256": hashlib.sha256(Path(args.experiment).read_bytes()).hexdigest(),
        "git_sha": meta.get("git_sha"), "errors": errors,
        "evidence_boundary": "Historical synthetic task family reused for calibration; NOT independent confirmatory evidence. GO is pilot readiness only; never an ACL effect claim.",
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
