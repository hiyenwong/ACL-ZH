# Result Report: local-deepseek-r1-8b-dependency-mirror-edit-content-v0.4

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
Experiment: benchmark/local-model/experiment-deepseek-r1-8b-dependency-mirror-edit-content-v0.4.json
Manifest: benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
Git commit at run time: a5427db (worktree dirty flag recorded: true)
Temperature: 0 / Top-p: 1 / Seed: 20261011
Max tokens: 4096 (Amendment A1; the 4B/12B runs used 256 — cross-model
  decoding-condition difference; within-model variant comparison unaffected)
Reasoning effort: none (requested; see truncation finding below)

Baseline: parsed 0/4, format compliant 0/4, tests 4/4, oracle 0/4, semantic success 0/4, task success 0/4
Minimal:  parsed 4/4, format compliant 1/4, tests 4/4, oracle 0/4, semantic success 0/4, task success 0/4
Full:     parsed 2/4, format compliant 1/4, tests 3/4, oracle 0/4, semantic success 0/4, task success 0/4

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

| Run | Task | Variant | finish_reason | completion_tokens | Category |
| ---: | --- | --- | --- | ---: | --- |
| 01 | dependency-anchor-01 | full | stop | 1730 | contract_failure (fence in content) |
| 02 | dependency-verbose-01 | baseline | stop | 3847 | contract_failure (no blocks) |
| 03 | dependency-no-target-file-01 | minimal | stop | 2950 | contract_failure (residual text) |
| 04 | dependency-no-file-ban-01 | baseline | stop | 3847 | contract_failure (no blocks) |
| 05 | dependency-anchor-01 | minimal | stop | 2950 | contract_failure (residual text) |
| 06 | dependency-no-target-file-01 | baseline | stop | 3847 | contract_failure (no blocks) |
| 07 | dependency-anchor-01 | baseline | length | 4095 | truncation (empty response) |
| 08 | dependency-no-file-ban-01 | full | length | 4095 | truncation (empty response) |
| 09 | dependency-verbose-01 | full | length | 4095 | truncation (empty response) |
| 10 | dependency-verbose-01 | minimal | stop | 4004 | semantic_failure |
| 11 | dependency-no-file-ban-01 | minimal | stop | 2950 | contract_failure (residual text) |
| 12 | dependency-no-target-file-01 | full | stop | 2984 | semantic_failure |

Totals: contract_failure 7, truncation 3, semantic_failure 2, success 0.
No constraint violations.

## Result: floor run — 0/12 task success, 0/12 semantic success

No variant produced a single hidden-oracle pass. This is a floor
result on this task family for this model condition; the run is
**non-discriminating** (zero everywhere), reported as such per the
preregistration.

Observations (descriptive only, n=4 tasks, no significance claim):

- All three truncated runs consumed 4095/4096 completion tokens with
  empty content. This forced-reasoning model spends the completion
  budget on reasoning tokens despite `reasoning_effort: none`; the
  4096-token budget pinned by Amendment A1 was still exhausted in 3/12
  runs (and 19/36 on the constraint manifest). A large share of this
  experiment measured budget exhaustion, not task ability.
- Baseline never emitted a parseable block in any non-truncated run
  (all `no_file_blocks`); Minimal and Full sometimes did. With 0
  oracle passes everywhere, this difference stays at the format level
  and supports no task-success claim.
- Identical completion-token counts across tasks sharing prompt text
  (e.g. 3847 for three baseline runs) are consistent with
  deterministic decoding at temperature 0 — repetitions would not be
  independent evidence.

## Interpretation within the evidence boundary

- Combined with the gemma-3-4b floor (0/12) and gemma-4-12b ceiling
  (12/12) on the same manifest, this 8B run adds a third
  non-discriminating point: the dependency-mirror family still shows
  no observable Baseline / Minimal / Full separation at any tested
  model strength.
- The ~7B/8B intermediate-capability hypothesis remains an
  experiment-selection hypothesis; this run neither confirms a
  discriminating band nor rules one out, because 25% of runs truncated
  and the rest failed semantically at the oracle.
- Cross-model comparisons carry the Amendment A1 caveat: max_tokens
  4096 here vs 256 for the 4B/12B runs, and this model is a
  forced-reasoning build; within-model paired comparison is the only
  primary analysis, and it shows nothing.
- Never merge with strict unified-diff counts; not comparable with
  agent-CLI tracks.
