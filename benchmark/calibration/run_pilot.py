#!/usr/bin/env python3
"""Read committed model condition; prevent accidental parameter or workspace drift."""
import argparse
import hashlib
import tempfile
import json
import subprocess
import sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    ap.add_argument("--hardware-note", default=None)
    a = ap.parse_args()
    exp = json.loads(Path(a.experiment).read_text(encoding="utf-8"))
    if exp.get("model") in ("MODEL_NOT_PINNED", None) or exp.get("status") != "PINNED_PENDING_COMMIT_AND_CONTROL":
        ap.error("experiment model condition is not pinned")
    if exp.get("variants") != ["baseline"]:
        ap.error("not baseline-only")
    if Path(a.workdir).exists():
        ap.error("workdir exists; use a fresh path, never overwrite historical responses")
    root = Path(__file__).resolve().parents[2]
    check = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
    if check.returncode or check.stdout.strip():
        ap.error("git worktree must be clean BEFORE generation")
    cmd = [sys.executable, str(root / "benchmark/local-model/run_lm_studio.py"),
           "--base-url", a.base_url, "--model", exp["model"],
           "--experiment", a.experiment, "--manifest", a.manifest,
           "--workdir", a.workdir,
           "--exporter", str(root / "benchmark/local-model/export_edit_content_prompts.py"),
           "--temperature", str(exp["decoding"]["temperature"]),
           "--top-p", str(exp["decoding"]["top_p"]),
           "--seed", str(exp["decoding"]["seed"]),
           "--max-tokens", str(exp["decoding"]["max_tokens"]),
           "--quantization", exp["quantization"],
           "--context-length", str(exp["context_length"])]
    if exp["decoding"].get("reasoning_effort") is not None:
        cmd.extend(["--reasoning-effort", exp["decoding"]["reasoning_effort"]])
    if a.hardware_note:
        cmd.extend(["--hardware-note", a.hardware_note])
    subprocess.run([sys.executable, str(Path(__file__).with_name("validate_pilot.py")),
                    "--experiment", a.experiment, "--manifest", a.manifest], check=True)

    # Fresh exact-manifest controls required before scored inference.
    with tempfile.TemporaryDirectory(prefix="aclzh-calibration-controls-") as td:
        summary = {}
        eval_script = root / "benchmark/agent-eval/run.py"
        reference = root / "benchmark/agent-eval/reference_agent.py"
        controls = [
            ("noop", "true"),
            ("reference", 'python "' + str(reference) + '" "{prompt_file}"'),
        ]
        for label, command in controls:
            output = Path(td) / label
            subprocess.run([sys.executable, str(eval_script),
                            "--manifest", a.manifest, "--variant", "full",
                            "--agent", label, "--agent-command", command,
                            "--repetitions", "1", "--output", str(output)], check=True)
            rows = [json.loads(line)
                    for p in output.glob("*.jsonl")
                    for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
            passed = sum(bool(row["task_success"]) for row in rows)
            n = len(exp["tasks"])
            expected = n if label == "reference" else 0
            if len(rows) != n or passed != expected:
                ap.error(label + " control failed: " + str(passed) + "/" + str(len(rows)))
            summary[label] = {"n": n, "success": passed}
        summary["manifest_sha256"] = hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest()
        Path(a.workdir).mkdir(parents=True, exist_ok=False)
        (Path(a.workdir) / "control-evidence.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
