# Result Report: local-gemma3-4b-dependency-mirror-edit-content-v0.4

Run date: 2026-10-14

```text
Model: google/gemma-3-4b
Quantization: 4bit (variant google/gemma-3-4b@4bit)
LM Studio version: lms CLI commit 69d945a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-gemma3-4b-dependency-mirror-edit-content-v0.4.json
Manifest: benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
Git commit at run time: 716b39a
Temperature: 0 / Top-p: 1 / Seed: 20261011 / Max tokens: 256

Baseline: parsed 1/4, format compliant 1/4, task success 0/4
Minimal:  parsed 1/4, format compliant 1/4, task success 0/4
Full:     parsed 4/4, format compliant 4/4, task success 0/4

Evidence boundary: diagnostic track; never merge with strict diff counts.
```

## Variant separation in format compliance (not in task success)

This is the first local run with ANY variant separation:

- Full ACL prompts produced a parseable, contract-shaped response in
  4/4 runs; Baseline and Minimal did so in only 1/4 each.
- However, Full's blocks wrap the file content in ```python fences.
  The frozen parser captures the fences as content, the written file
  is invalid Python, and visible tests fail (0/4 under Full).
- Baseline/Minimal mostly emit the post-hoc shape `<<<path>>>` +
  fenced block (missing the `FILE:` marker), which the frozen parser
  correctly rejects.
- Hidden oracle: 0/12 in all variants. Even the correctly-headed Full
  blocks would need fence-free content to be scored semantically; the
  one inspected Full response had the intended edit inside the fences.

Interpretation, within the evidence boundary: for this weak model the
structured Full prompt measurably improves response-contract
*following* (header shape), but the model still violates the contract
in content (fences), and no semantic correctness signal is observable
at this ability level. This is a format-compliance variant effect, not
a task-success effect.

## Comparison boundary

- Not comparable with strict diff counts (different track).
- Pairs with the gemma-4-12b edit-content run on the same tasks:
  4B fails everywhere, 12B succeeds 12/12 — the task family sits
  between these two models' abilities under this contract.
