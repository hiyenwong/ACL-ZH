# Information-equivalent edit-content v0.1: completed result

Run: `c7ab1518-ab20-472c-8c6e-fcf67bf71206`. Experiment:
`77ca4793-b1c2-424c-9c15-daaa022b2b92`. Commit: `082d13c`.

## Interpretation

After machine-checked information equivalence, the three prompt presentations
did not separate at the preregistered follow-up gate. Baseline scored 11/12,
Minimal ACL 10/12, and Full ACL 10/12 on contract `task_success`. The paired
differences are only Baseline +1 over Minimal and Baseline +1 over Full;
Minimal and Full have identical task outcomes. The preregistered follow-up gate
required at least four net paired wins and was not met.

All five failures were budget-exhaustion truncations. Each used 16,383
completion tokens, reported 16,382 hidden reasoning tokens, returned zero
visible characters, and therefore had no file blocks. All 31 non-truncated
calls passed both semantics and format. The 11/10/10 split is therefore a
distribution of reasoning-budget exhaustion, not evidence of an ACL structure
effect. The observed truncation rate is 5/36, below the preregistered 12/36
truncation-confounded threshold, but it accounts for every failure in this run.

No ACL effectiveness, harm, or statistical-significance claim is supported.
This is one deterministic local-model run on 12 fresh tasks, with no repetition
inflation and no pooling with historical unequal-information manifests.

## Primary outcome

| Variant | Task success | Semantic success | Format compliance | Parsed | Truncated |
|---|---:|---:|---:|---:|---:|
| Baseline | 11/12 | 11/12 | 11/12 | 11/12 | 1/12 |
| Minimal ACL | 10/12 | 10/12 | 10/12 | 10/12 | 2/12 |
| Full ACL | 10/12 | 10/12 | 10/12 | 10/12 | 2/12 |

Paired task-success discordance:

- Baseline vs Minimal: 2 Baseline-only wins, 1 Minimal-only win (net +1).
- Baseline vs Full: 2 Baseline-only wins, 1 Full-only win (net +1).
- Minimal vs Full: 0 discordant tasks.

## Truncated calls

| Task | Variant |
|---|---|
| eq-retry-01 | Minimal |
| eq-retry-01 | Full |
| eq-window-01 | Minimal |
| eq-window-01 | Full |
| eq-slug-01 | Baseline |

All five rows have `finish_reason: length`, `response_chars: 0`, and
`format_violations: ["no_file_blocks"]`. No completed response failed visible
tests, hidden oracle, scope, parser, or response-contract checks.

## Validation and reproducibility

Before inference, the strict information-equivalence audit passed all 12 tasks
and 56 counted technical facts. No-op controls were 0/36 across the three
variants; reference controls were 36/36. Generation preserved all 36 raw
responses and run-order metadata. Scoring provenance was `verified` without an
override. The effective generation metadata records the fixed 8B model, 4bit
quantization, context length 32,768, temperature 0, top-p 1, seed 20261011,
16,384 maximum completion tokens, and requested reasoning effort `none`.

The immediately preceding submitted run failed after LM Studio unloaded the
model during request 6. Its five partial generations were never scored and are
not pooled with this result.

## Decision

Freeze this node as completed. Do not launch a fresh ACL-presentation
replication from this single +1 paired difference. If the project continues
with this model, the next defensible line is budget/reasoning control or a
fresh harder held-out set; do not retune the budget or response protocol on
these 12 tasks and then present the same set as an independent confirmation.

Evidence: [aggregate](equivalence/aggregate-edit-content.json);
[structured analysis](analysis-summary.json);
[generation metadata](equivalence/generation-metadata.json);
[audit](pre-inference-equivalence-audit.json);
[no-op controls](controls-noop.json);
[reference controls](controls-reference.json);
[preregistration](PREREG-INFORMATION-EQUIVALENT-V0.1.md).
