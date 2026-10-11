# Result Report: local-gemma3-4b-dependency-mirror-v0.4

Date: 2026-10-11

```text
Model: google/gemma-3-4b
Quantization: 4bit (variant google/gemma-3-4b@4bit)
LM Studio version: lms CLI commit 69d945a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-gemma3-4b-dependency-mirror-v0.4.json
Manifest: benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
Git commit: 0011899
Temperature: 0
Top-p: 1
Seed: 20261011
Max tokens: 256

Baseline task success: 0/4
Minimal task success: 0/4
Full task success: 0/4

Baseline patch apply: 0/4
Minimal patch apply: 0/4
Full patch apply: 0/4

Normalized diagnostic: fence-only normalization changed no outcome
  (0/4 patch apply in every variant, strict and normalized)
Notable failures: all 12 responses fail `git apply` with
  "corrupt patch" (invalid hunk headers / fabricated hunk shapes).
  Inspected samples also show semantic failure independent of
  serialization: run 02 (dependency-anchor-01:full) deletes the
  `def dumps(value):` signature line; run 05
  (dependency-anchor-01:baseline) removes the function definition
  and rewrites the test file, which was not a requested change.
Evidence boundary: see below.
```

## Determinism observation

Identical prompts produced byte-identical responses (temperature 0,
fixed seed): the baseline runs for dependency-anchor-01,
dependency-no-file-ban-01 and dependency-no-target-file-01 share one
SHA-256, and their minimal runs share another. This is consistent
with the mirror design — the anchor / no-file-ban / no-target-file
factors only differ in the full variant — and confirms the runtime
honors deterministic decoding. Per R9, repeating this exact
configuration is not independent evidence.

## Evidence boundary

- This is a **new model condition**. It is NOT comparable with the
  Qwen2.5-Coder-3B dependency-mirror experiment: different model
  family (Gemma 3 4B, not coder-tuned), different quantization,
  different inference backend (LM Studio OpenAI-compatible server
  vs HF transformers).
- The 0/12 outcome is consistent with a patch-serialization floor
  combined with genuine task-solving failure; it does not separate
  the two cleanly, and it says nothing about ACL-ZH effectiveness.
- Tool-path status: the LM Studio runner and scorer executed
  end-to-end (export → 12 stateless requests → raw archival →
  strict + normalized scoring → aggregate). The path itself is
  validated by this run.
