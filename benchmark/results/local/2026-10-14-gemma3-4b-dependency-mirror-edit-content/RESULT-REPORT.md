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

Baseline: parsed 1/4, format compliant 0/4, tests 3/4*, oracle 0/4, semantic success 0/4, task success 0/4
Minimal:  parsed 1/4, format compliant 0/4, tests 3/4*, oracle 0/4, semantic success 0/4, task success 0/4
Full:     parsed 4/4, format compliant 0/4, tests 0/4, oracle 0/4, semantic success 0/4, task success 0/4

*Unparseable responses write nothing, so visible tests run against the
unmodified fixture and pass for 3 of 4 tasks; the hidden oracle catches
the no-op (0/12 everywhere). tests-pass here must not be read as
progress toward success.

Re-scored 2026-10-15 with the remediated format_compliant detector
(any Markdown fence line — ``` or ~~~ — in block content, duplicate
file paths, and empty paths are now contract violations; parser itself
untouched, raw responses unchanged). Metric definitions:
semantic_task_success = visible tests AND hidden oracle AND no
constraint violation; task_success = semantic_task_success AND
format_compliant.

Evidence boundary: diagnostic track; never merge with strict diff counts.
```

## No variant separation after format_compliant remediation

The originally reported "Full ACL format compliance 4/4 vs 1/4" does
NOT survive the corrected contract detection and has been removed as a
conclusion:

- All 4 Full responses wrap the file content in ```python fences. The
  frozen parser captures the fences as content; content wrapped in a
  Markdown fence is not "complete final file content", so every Full
  response is a contract violation (format_compliant 0/4).
- The single parsed Baseline and Minimal responses have the same
  fence-wrapped content defect, so Baseline/Minimal are also 0/4
  compliant (previously mis-scored 1/4).
- What remains observable is only header-shape separation: Full prompts
  produced a well-formed `<<<FILE:...>>>` block header in 4/4 runs vs
  1/4 for Baseline/Minimal (the rest use the post-hoc `<<<path>>>`
  shape). A well-formed header with non-compliant content is still a
  contract failure, so this is NOT a format-compliance variant effect
  and not evidence of any ACL benefit.
- Hidden oracle: 0/12 in all variants; semantic_task_success 0/12;
  task_success 0/12.

Interpretation, within the evidence boundary: for this weak model, no
variant produces a single contract-compliant or semantically correct
response. There is no variant signal of any kind in this run.

## Comparison boundary

- Not comparable with strict diff counts (different track).
- Pairs with the gemma-4-12b edit-content run on the same tasks:
  4B fails everywhere, 12B succeeds 12/12 — the task family sits
  between these two models' abilities under this contract.

## Provenance hardening re-score (2026-10-18)

Re-scored with the P2-02 provenance-aware scorer on the unchanged raw
responses. The aggregate now records the exact scoring implementation
(`scorer_sha256`, `oracle_sha256`, `parser_sha256`) and the actual input
hashes. This run predates generation-time provenance capture, so the
aggregate is labeled `status: unpinned_baseline`, `score_kind: rescore`.
No count changed; the interpretation above is unaffected.
