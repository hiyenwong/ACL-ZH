#!/usr/bin/env python3
"""Pin calibration model settings BEFORE running LM Studio inference."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "experiments/experiment-baseline-pilot-v0.1.template.json"
DEST = HERE / "experiments/experiment-baseline-pilot-v0.1.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--quantization", required=True)
    ap.add_argument("--context-length", type=int, required=True)
    ap.add_argument("--max-tokens", type=int, required=True)
    ap.add_argument("--reasoning-effort", default="none")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.model == "MODEL_NOT_PINNED" or not a.quantization.strip():
        ap.error("exact model and quantization must be pinned")
    if a.context_length <= 0 or a.max_tokens <= 0:
        ap.error("context-length and max-tokens must be positive")
    if DEST.exists() and not a.force:
        ap.error("pinned experiment already exists; do not overwrite silently")
    exp = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    exp["model"] = a.model
    exp["quantization"] = a.quantization
    exp["context_length"] = a.context_length
    exp["decoding"]["max_tokens"] = a.max_tokens
    exp["decoding"]["reasoning_effort"] = None if a.reasoning_effort == "server-default" else a.reasoning_effort
    exp["status"] = "PINNED_PENDING_COMMIT_AND_CONTROL"
    DEST.write_text(json.dumps(exp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {DEST}. Review and COMMIT this file BEFORE scored inference.")

if __name__ == "__main__":
    main()
