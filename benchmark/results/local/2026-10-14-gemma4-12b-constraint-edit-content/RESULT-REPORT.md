# Result Report: local-gemma4-12b-constraint-edit-content-v0.3

Run date: 2026-10-14

```text
Model: google/gemma-4-12b-qat
Quantization: Q4_0 (QAT, variant google/gemma-4-12b-qat@q4_0)
LM Studio version: lms CLI commit 69d945a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-gemma4-12b-constraint-edit-content-v0.3.json
Manifest: benchmark/tasks/manifest-constraint-v0.3.jsonl
Git commit at run time: 716b39a
Temperature: 0 / Top-p: 1 / Seed: 20261011 / Max tokens: 256
Reasoning effort: none

Baseline: parsed 12/12, format compliant 12/12, tests 12/12, oracle 11/12, task success 11/12
Minimal:  parsed 12/12, format compliant 12/12, tests 12/12, oracle 11/12, task success 11/12
Full:     parsed 12/12, format compliant 12/12, tests 12/12, oracle 11/12, task success 11/12

Evidence boundary: diagnostic track; never merge with strict diff counts.
```

## Uniform result: 33/36, no variant separation

Every run produced a parseable, contract-compliant response. The only
failing task is `constraint-return-01`, which fails the hidden oracle
in all three variants while passing visible tests.

Diagnosis of constraint-return-01: the oracle requires
`parse_id(" ID-42 ") == 42` (whitespace stripping before prefix
removal). The model's deterministic implementation handles the `ID-`
prefix but never strips surrounding whitespace, in all three variants
— `int(" ID-42 ")` raises. The task's discriminative design (visible
tests pass, hidden oracle checks the constraint) works as intended;
the prompt variant made no observable difference for this model.

## Interpretation within the evidence boundary

- The constraint-focused task family is also near-saturated for a
  12B-class model under the file-content contract: 11/12 everywhere.
- No Baseline / Minimal / Full separation is observable at this model
  strength. Together with the dependency-mirror edit-content run
  (12/12 saturation), local evidence so far says: once serialization
  is removed, these task sets do not discriminate prompt variants for
  models at or above ~12B.
- The one discriminating task (constraint-return-01) fails uniformly,
  so it separates "exact constraint following" from "plausible
  implementation", but not prompt variants.
- Not comparable with the Qwen 3B constraint v0.3 diff-track counts
  (different model, backend, contract) and never mergeable with
  strict unified-diff results.
