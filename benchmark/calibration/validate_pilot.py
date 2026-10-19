#!/usr/bin/env python3
"""Validate M2-01 pilot manifest, freeze contract, and no-op oracle controls."""
import argparse
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agent_eval", ROOT / "agent-eval" / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def validate(manifest, experiment):
    errors = []
    tasks = [json.loads(s) for s in Path(manifest).read_text(encoding="utf-8").splitlines() if s.strip()]
    exp = json.loads(Path(experiment).read_text(encoding="utf-8"))
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)) or not ids:
        errors.append("duplicate/empty task IDs")
    if len(tasks) != 12:
        errors.append("pilot requires 12 existing task-oracle IDs")
    if exp.get("variants") != ["baseline"] or exp.get("tasks") != ids:
        errors.append("experiment must use exactly the manifest IDs and baseline variant")
    if exp.get("run_order") != [t + ":baseline" for t in ids]:
        errors.append("run order must match manifest baseline order")
    if exp.get("repetitions") != 1:
        errors.append("one repetition required")
    for t in tasks:
        for field in ("id", "category", "fixture", "baseline", "allowed_paths", "forbidden_paths", "test_command", "oracle"):
            if field not in t: errors.append(f"{t.get('id')}: missing {field}")
        if not t.get("allowed_paths"):
            errors.append(f"{t['id']}: empty allowed paths")
        if set(t.get("allowed_paths", [])) & set(t.get("forbidden_paths", [])):
            errors.append(f"{t['id']}: allowed/forbidden overlap")
    with tempfile.TemporaryDirectory(prefix="aclzh-calibration-control-") as td:
        ws = Path(td)
        runner.write_fixture(ws)
        for t in tasks:
            if runner.hidden_oracle(t["id"], ws):
                errors.append(f"{t['id']}: no-op unexpectedly passes oracle")
    return {"status": "FAIL" if errors else "PASS", "tasks": len(tasks),
            "no_op": "0/" + str(len(tasks)) if not errors else "FAILED",
            "reference_control": "NOT RE-EXECUTED; historical CI is not a substitute for new controls",
            "errors": errors}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--experiment", required=True)
    args = ap.parse_args()
    result = validate(args.manifest, args.experiment)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
