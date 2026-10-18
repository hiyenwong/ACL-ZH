# Preregistration: Next Discriminating Local Experiment (~7B)

Prereg ID: `prereg-next-discriminating-v0.1`
Date: 2026-10-19
Status: **preregistered — no inference run under this protocol yet**
Priority: P2-03 (per `benchmark/tasks/POST-REMEDIATION-REVIEW-V0.2.md`)

This document freezes the protocol for the next local-model experiment
**before** any inference. Once the experiment JSON is committed, every
field it pins is frozen for that experiment.

## 1. Research question and hypothesis status

Question: on the current task families, does a mid-capability local
model show any Baseline / Minimal ACL / Full ACL separation that the
tested 4B (floor) and 12B (ceiling) conditions cannot?

The tested 4B and 12B conditions suggest that an intermediate
capability range may provide more discrimination on the current tasks.
A ~7B model is a reasonable next test condition. **This is an
experiment-selection hypothesis, not a validated capability threshold.**
Both a real variant effect and a reproducible null result are valid
outcomes; a null result will be labeled a null result.

## 2. Tracks and predefined outcomes

- Primary track: **edit-content diagnostic** (`local-lm-studio-edit-content`,
  contract `edit-content-contract-v0.1`).
- The strict unified-diff track is a separate predefined outcome family
  and is NOT part of this experiment's success metrics; if strict-diff
  runs are also executed, they are reported separately and never merged.
- Predefined endpoints per variant:
  - primary: `task_success` (= `semantic_task_success` AND
    `format_compliant`);
  - secondary: `semantic_task_success`, `format_compliant`;
  - diagnostics: parsed block count, per-category format violations.

## 3. Fixed conditions

- Manifests: `benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl`
  (12 runs) AND `benchmark/tasks/manifest-constraint-v0.3.jsonl`
  (36 runs), identical to the existing 4B/12B runs for comparability.
  Both manifests' No-op 0/N and Reference N/N controls must pass in CI
  before scored inference.
- Variants: baseline / minimal / full; per-task paired comparison
  (same task under all three variants).
- Decoding: temperature 0, top_p 1, seed 20261011, max_tokens 256,
  reasoning effort pinned in the experiment file (`none` unless the
  model does not support it — pinned explicitly either way).
- Fresh chat per run (stateless calls; the runner never carries
  context between runs).
- Repetitions: 1 per task×variant. Identical deterministic generations
  are NOT independent replications; no repetition-count inflation.
- Model: exact identifier + quantization + context length pinned in the
  committed experiment JSON **before** inference. Quantization and
  context length are recorded verbatim, never inferred from the model
  name. Unknown fields stay `null`.
- Run order: randomized with seed 20261011, recorded in the experiment
  JSON.
- Provenance: generation metadata carries the full provenance block;
  scoring runs fail closed on any hash mismatch (no override for a
  promotion-grade run).

## 4. Predefined failure categories

Per run, exactly one primary classification:

1. `contract_failure` (format violation: no_file_blocks,
   markdown_fence_in_content, duplicate_file_path, empty_file_path,
   residual_text, protocol violation);
2. `semantic_failure` (contract-compliant but visible tests or hidden
   oracle fail);
3. `constraint_violation` (forbidden/unrequested write);
4. `truncation` (response hits max_tokens — detected via usage stats /
   missing `<<<END>>>`);
5. `success` (task_success).

## 5. Analysis plan (fixed before inference)

- Report raw counts and the full per-task × variant outcome matrix for
  each manifest separately; no pooling across manifests.
- Variant comparison is paired at the task level (same task, three
  variants). With n=4 tasks (dependency-mirror) and n=12 tasks
  (constraint), no formal significance claim will be made; any observed
  difference is reported as a small-sample observation with per-task
  detail, not as an effect size.
- A variant-separation claim requires the same direction on BOTH
  manifests; a single-manifest difference is labeled exploratory.
- Ceiling/floor conditions are recorded explicitly (saturation or
  zero everywhere = non-discriminating run, reported as such).
- No result-dependent modification of scorer, parser, oracle,
  manifests, or prompts. Any discovered defect stops the experiment;
  results gathered before the fix are labeled exploratory.

## 6. Promotion gate (before results enter README)

- raw responses preserved and count-verified;
- run order and metadata verified;
- provenance `status: verified` (no override) at scoring;
- controls green on the exact manifests used;
- format compliance, semantic success, and contract task success
  reported separately;
- wording constraints: the ~7B condition is never described as a
  validated threshold; no ACL-ZH effectiveness claim without
  reproducible, non-ceiling/non-floor, multi-task separation.

## 7. What this preregistration does not do

- It does not select the exact model build (pinned later in the
  committed experiment JSON, before inference).
- It does not schedule rule ablation: ablation remains gated on a real
  positive variant signal.
- It does not change any historical result or the contract version.
