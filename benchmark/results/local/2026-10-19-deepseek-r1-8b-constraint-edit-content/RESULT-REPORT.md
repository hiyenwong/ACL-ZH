# Result Report: local-deepseek-r1-8b-constraint-edit-content-v0.3

Run date: 2026-10-19 (generation metadata recorded 2026-10-18T17:22Z, UTC)

Preregistered under `benchmark/local-model/PREREG-NEXT-DISCRIMINATING-V0.1.md`
including **Amendment A1** (pinned before any scored inference, commit
`a5427db`). The ~7B hypothesis is tested with the only available
intermediate-size local model, `deepseek/deepseek-r1-0528-qwen3-8b`
(**8B chosen as the available intermediate point — not a validated
capability threshold**).

```text
Model: deepseek/deepseek-r1-0528-qwen3-8b (forced-reasoning model)
Quantization: 4bit (recorded verbatim from LM Studio native API)
Context length: 131072 (recorded verbatim)
LM Studio version: lms CLI commit dcefd5a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-deepseek-r1-8b-constraint-edit-content-v0.3.json
Manifest: benchmark/tasks/manifest-constraint-v0.3.jsonl
Git commit at run time: a5427db (worktree dirty flag recorded: true)
Temperature: 0 / Top-p: 1 / Seed: 20261011
Max tokens: 4096 (Amendment A1; the 4B/12B runs used 256 — cross-model
  decoding-condition difference; within-model variant comparison unaffected)
Reasoning effort: none (requested; see truncation finding below)

Baseline: parsed 1/12, format compliant 0/12, tests 11/12, oracle 0/12, semantic success 0/12, task success 0/12
Minimal:  parsed 4/12, format compliant 2/12, tests 12/12, oracle 1/12, semantic success 1/12, task success 1/12
Full:     parsed 3/12, format compliant 0/12, tests 9/12, oracle 1/12, semantic success 0/12, task success 0/12

Metric definitions (contract edit-content-contract-v0.1):
semantic_task_success = visible tests AND hidden oracle AND no
constraint violation; task_success = semantic_task_success AND
format_compliant (no residual text, no protocol violation, no
duplicate/empty file path, no Markdown fence line in block content).

Scoring provenance: status verified, score_kind initial, no overrides.
Evidence boundary: diagnostic track; never merge with strict diff counts.
```

## Primary failure classification (prereg §4, one category per run)

Precedence: truncation (finish_reason=length) > constraint_violation >
contract_failure > semantic_failure > success.

| Category | baseline | minimal | full | total |
| --- | ---: | ---: | ---: | ---: |
| truncation | 7 | 3 | 9 | 19 |
| contract_failure | 5 | 7 | 3 | 15 |
| semantic_failure | 0 | 1 | 0 | 1 |
| success | 0 | 1 | 0 | 1 |
| constraint_violation | 0 | 0 | 0 | 0 |

The single success is `constraint-side-effect-01` (minimal). The single
semantic-but-not-task case is `constraint-api-01` (minimal):
format-compliant and tests pass, but the hidden oracle fails. One
further run (`constraint-api-01`, full) passed the hidden oracle yet
failed visible tests — semantic_task_success requires both, so it does
not count.

19 of 36 runs (53%) truncated: `finish_reason: length` with
4095/4096 completion tokens consumed, 18 of them with completely empty
content (one, `constraint-schema-01` full, emitted 93 chars without a
closing marker). This forced-reasoning model spends the completion
budget on reasoning tokens despite `reasoning_effort: none`; the
4096-token budget pinned by Amendment A1 was still exhausted in over
half of the runs. **The majority of this experiment measured budget
exhaustion, not task ability.**

## Variant comparison (paired per task, small sample)

Per the preregistration, a variant-separation claim requires the same
direction on BOTH manifests. The dependency-mirror companion run is a
complete floor (0/12 everywhere, no variant difference). The single
Minimal success here is therefore labeled **exploratory**: one task,
one manifest, n=12 per variant with no formal significance claim.

Truncation frequency itself differs by variant (baseline 7/12,
minimal 3/12, full 9/12): longer structured prompts correlate with
more reasoning-token exhaustion in this model. Because truncated runs
are failures on every variant, this pattern changes failure
*composition*, not success counts, and is reported as a small-sample
observation only.

Notable per-task behavior:

- `constraint-return-01` fails the hidden oracle in all three variants
  (baseline/minimal contract failures, full truncation) — the same
  uniform failure seen with gemma-4-12b; the task's discriminating
  design replicates.
- `dependency-01`, the only task where the Qwen2.5-Coder-3B diff track
  ever succeeded (Full ACL), shows no success here in any variant
  under the edit-content contract.

## Interpretation within the evidence boundary

- Near-floor result: 1/36 task success. No reproducible variant
  signal; the exploratory Minimal single-task observation does not
  meet the preregistered both-manifests rule.
- Together with the dependency-mirror floor, this 8B condition is
  **non-discriminating** on both manifests, reported as such.
- The ~7B/8B intermediate-capability hypothesis remains an
  experiment-selection hypothesis. The 53% truncation rate limits what
  this run can say even within-model: a future discriminative test of
  a reasoning-style model needs a decoding configuration that actually
  contains reasoning spend (larger budget or a runtime honoring
  reasoning-effort control), and any such rerun is a different
  decoding condition that must be pinned by a new amendment before
  inference.
- Cross-model comparisons carry the Amendment A1 caveat (max_tokens
  4096 vs 256 for the 4B/12B runs; forced-reasoning build).
- Never merge with strict unified-diff counts; not comparable with
  agent-CLI tracks.
