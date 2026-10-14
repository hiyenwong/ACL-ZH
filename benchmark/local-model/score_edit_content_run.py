#!/usr/bin/env python3
"""Score an LM Studio edit-content diagnostic run.

Parses each raw response with the frozen edit-content parser
(edit_content_parser.py), writes parsed files into a fresh fixture,
and applies the same visible tests + hidden oracle + forbidden-path +
unrequested-change checks as the strict diff track.

This is a DIAGNOSTIC track. Its rows use track label
"local-lm-studio-edit-content" and must never be merged with strict
unified-diff results. There is no normalized variant: the parser is
frozen before execution, and format failures are the measurement.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "agent-eval" / "run.py"
spec = importlib.util.spec_from_file_location("aclzh_runner", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

PARSER_SPEC = importlib.util.spec_from_file_location(
    "edit_content_parser", Path(__file__).with_name("edit_content_parser.py")
)
parser = importlib.util.module_from_spec(PARSER_SPEC)
PARSER_SPEC.loader.exec_module(parser)

TRACK = "local-lm-studio-edit-content"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def score_response(task, response, model):
    with tempfile.TemporaryDirectory(prefix="aclzh-edit-content-") as td:
        ws = Path(td)
        runner.write_fixture(ws)
        protected = {p: runner.sha(ws / p) for p in task.get("forbidden_paths", [])}
        runner.sh("git init -q && git config user.email benchmark@example.invalid "
                  "&& git config user.name benchmark && git add . && git commit -qm baseline", ws)

        blocks = parser.extract_file_blocks(response)
        allowed = set(task.get("allowed_paths", []))
        forbidden = set(task.get("forbidden_paths", []))
        parsed_paths = []
        protocol_violations = []
        for path, content in blocks:
            parsed_paths.append(path)
            if path not in allowed:
                protocol_violations.append(path)
                continue
            target = ws / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        # Capture changed files BEFORE running tests: unittest creates
        # __pycache__ artifacts that must not count as model changes.
        changed = runner.git_changed(ws)
        start = time.time()
        tests = runner.sh(task["test_command"], ws, timeout=120)
        elapsed = time.time() - start
        oracle_ok = runner.hidden_oracle(task["id"], ws)
        forbidden_changed = [p for p in forbidden if p in changed]
        unrequested = [p for p in changed if allowed and p not in allowed]
        constraint_violation = bool(forbidden_changed or unrequested or protocol_violations)
        success = tests.returncode == 0 and oracle_ok and not constraint_violation
        format_compliant = bool(blocks) and not parser.residual_text(response) and not protocol_violations

        return {
            "task_id": task["id"], "category": task["category"], "track": TRACK,
            "variant": None, "agent": "openai-compatible-chat-completions",
            "provider": "lm-studio-local", "model": model, "repetition": 0,
            "response_sha256": hashlib.sha256(response.encode()).hexdigest(),
            "elapsed_seconds": round(elapsed, 3),
            "parsed_file_count": len(blocks), "parsed_paths": parsed_paths,
            "format_compliant": format_compliant,
            "protocol_violations": protocol_violations,
            "changed_files": changed, "forbidden_path_changes": forbidden_changed,
            "unrequested_changes": unrequested,
            "visible_tests_exit_code": tests.returncode,
            "visible_tests_pass": tests.returncode == 0,
            "hidden_oracle_pass": oracle_ok,
            "constraint_violation": constraint_violation,
            "task_success": success, "first_pass_success": success,
            "test_stdout": tests.stdout[-12000:], "test_stderr": tests.stderr[-12000:],
        }


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
    tasks = {t["id"]: t for t in
             (json.loads(x) for x in Path(args.manifest).read_text(encoding="utf-8").splitlines() if x.strip())}

    out = root / "results-edit-content.jsonl"
    out.unlink(missing_ok=True)
    rows = []
    for item in runs:
        response = (root / item["response"]).read_text(encoding="utf-8")
        row = score_response(tasks[item["task_id"]], response, model)
        row["variant"] = item["variant"]
        rows.append(row)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps({k: row[k] for k in
                          ("task_id", "variant", "parsed_file_count", "format_compliant",
                           "hidden_oracle_pass", "task_success")}, ensure_ascii=False), flush=True)

    summary = {}
    for variant in exp["variants"]:
        vs = [r for r in rows if r["variant"] == variant]
        summary[variant] = {
            "n": len(vs),
            "parsed": sum(r["parsed_file_count"] > 0 for r in vs),
            "format_compliant": sum(bool(r["format_compliant"]) for r in vs),
            "visible_tests_pass": sum(bool(r["visible_tests_pass"]) for r in vs),
            "hidden_oracle_pass": sum(bool(r["hidden_oracle_pass"]) for r in vs),
            "task_success": sum(bool(r["task_success"]) for r in vs),
        }

    matrix = {}
    for r in rows:
        matrix.setdefault(r["task_id"], {})[r["variant"]] = bool(r["task_success"])

    aggregate = {
        "experiment_id": exp["experiment_id"],
        "provider": "lm-studio-local",
        "track": TRACK,
        "model": model,
        "runs": len(rows),
        "summary": summary,
        "task_matrix": matrix,
        "evidence_boundary": "Diagnostic edit-content track; not comparable with "
                             "strict unified-diff task-success counts.",
    }
    (root / "aggregate-edit-content.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
