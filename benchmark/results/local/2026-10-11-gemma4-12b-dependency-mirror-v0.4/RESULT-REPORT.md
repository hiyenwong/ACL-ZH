# Result Report: local-gemma4-12b-dependency-mirror-v0.4

Run date: 2026-10-11

```text
Model: google/gemma-4-12b-qat
Quantization: Q4_0 (QAT, variant google/gemma-4-12b-qat@q4_0)
LM Studio version: lms CLI commit 69d945a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-gemma4-12b-dependency-mirror-v0.4.json
Manifest: benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
Git commit at run time: 3ac57e3
Temperature: 0
Top-p: 1
Seed: 20261011
Max tokens: 256
Reasoning effort: none (see below)

Baseline task success: 0/4
Minimal task success: 0/4
Full task success: 0/4

Baseline patch apply: 0/4
Minimal patch apply: 0/4
Full patch apply: 0/4

Normalized diagnostic: fence-only normalization changed no outcome
  (0/4 patch apply in every variant, strict and normalized)
Notable failures: see diagnosis below — this run is NOT a semantic
  floor; it is a pure patch-serialization floor.
Evidence boundary: see below.
```

## Decoding deviation: reasoning_effort=none

A first attempt under the protocol default left the server-side
reasoning behavior untouched: the model spent 253/256 completion tokens
on `reasoning_content` and returned empty content on every run. That
attempt measured budget exhaustion, not the task, and was aborted after
2 runs; its partial outputs were discarded.

The scored run passes `reasoning_effort: "none"` (supported by the LM
Studio server for this model; verified: `reasoning_tokens: 0`). This is
a decoding change and is recorded in the experiment file's decoding
block per rule R4.

## Diagnosis: serialization floor over a correct edit

All 12 responses are byte-identical: the model deterministically
converges on one minimal patch regardless of variant. The edit content
is the semantically intended change
(`json.dumps(value, sort_keys=True, separators=(',', ':'))`).

The patch fails `git apply` for two format defects:

1. missing `a/` / `b/` path prefixes (`--- src/serializer.py` instead
   of `--- a/src/serializer.py`);
2. missing trailing newline at end of the response (git reports
   "corrupt patch" at the final hunk line).

Post-hoc diagnostic (separately labeled, NOT part of the scored
result): with only those two format defects repaired by hand, the patch
applies cleanly, passes the visible tests, and passes the hidden
oracle on all 4 tasks. So for this model on this task family, the
strict 0/12 is entirely a serialization-contract failure; the
underlying edit was correct in all 12 runs.

## Harness defect found during this diagnosis

`hidden_oracle()` in `benchmark/agent-eval/run.py` had no branch for
the four dependency-mirror task ids and fell through to `return False`,
so no v0.4 run could ever record `task_success`, regardless of output
quality. The mirror manifest had also never been covered by the
No-op/Reference control pair. Both gaps were fixed in the same session
(oracle alias mapping + CI control step; local controls after the fix:
No-op 0/4, Reference 4/4).

This defect did not distort any recorded v0.4 result: every scored run
so far (including this one) already failed at patch apply, where the
oracle is never reached.

## Evidence boundary

- New model condition. NOT comparable with the Qwen2.5-Coder-3B series
  or the gemma-3-4b run: different model family/size (Gemma 4 12B QAT),
  different quantization (Q4_0), LM Studio backend, and
  `reasoning_effort=none`.
- Allowed interpretation: "In this exact local experiment,
  gemma-4-12b-qat produced a semantically correct edit for all 12 runs
  but never emitted a directly `git apply`-compatible patch; no variant
  difference was observable because all responses were identical."
- Not allowed: any claim about ACL-ZH effectiveness. With zero
  variant separation in the responses, this run cannot speak to
  Baseline vs Minimal vs Full at all.
