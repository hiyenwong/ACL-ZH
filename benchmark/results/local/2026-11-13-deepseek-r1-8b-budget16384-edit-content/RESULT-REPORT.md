# Completed 8B budget-16384 diagnostic experiment

Date: 2026-11-13. Run: ad7d19bf-24d4-4ce8-88cf-ab5644a022e2.
Tracked source commit: 32678898e858f102bd9d64d0ab0916308b08ad65.
Model: deepseek/deepseek-r1-0528-qwen3-8b, reported 4bit.
Temperature 0, top_p 1, seed 20261011, max_tokens 16384,
requested reasoning_effort none. Configured context unknown.
48/48 raw responses preserved. Earlier interrupted attempts are not pooled.

## Outcome

No preregistered cross-manifest variant separation. Dependency-mirror remains
at a contract-success floor. Constraint is discriminating descriptively, with
Baseline above Minimal above Full; this does not establish causal harm from
ACL or a reproducible language effect. No formal significance claim.

## dependency-mirror

| Variant | n | Contract success | Semantic success | Format compliance |
|---|---:|---:|---:|---:|
| baseline | 4 | 0 | 1 | 0 |
| minimal | 4 | 0 | 3 | 0 |
| full | 4 | 0 | 1 | 2 |

Truncated: 0/12. Scoring provenance: verified, no overrides.

| Task | Baseline | Minimal | Full |
|---|---|---|---|
| dependency-anchor-01 | fail | fail | fail |
| dependency-verbose-01 | fail | fail | fail |
| dependency-no-target-file-01 | fail | fail | fail |
| dependency-no-file-ban-01 | fail | fail | fail |

[Aggregate](dependency-mirror/aggregate-edit-content.json) · [Generation metadata](dependency-mirror/generation-metadata.json)

## constraint

| Variant | n | Contract success | Semantic success | Format compliance |
|---|---:|---:|---:|---:|
| baseline | 12 | 8 | 9 | 8 |
| minimal | 12 | 6 | 9 | 6 |
| full | 12 | 4 | 6 | 5 |

Truncated: 1/36. Scoring provenance: verified, no overrides.

| Task | Baseline | Minimal | Full |
|---|---|---|---|
| constraint-schema-01 | pass | fail | fail |
| constraint-path-01 | pass | pass | pass |
| constraint-immutable-01 | pass | pass | fail |
| constraint-side-effect-01 | pass | pass | fail |
| constraint-stdlib-01 | fail | fail | fail |
| constraint-retry-01 | fail | fail | fail |
| scope-01 | pass | pass | fail |
| constraint-api-01 | pass | pass | pass |
| compatibility-01 | pass | pass | pass |
| dependency-01 | fail | fail | fail |
| constraint-return-01 | fail | fail | fail |
| exception-01 | pass | fail | pass |

[Aggregate](constraint/aggregate-edit-content.json) · [Generation metadata](constraint/generation-metadata.json)

## Validation and limitations

Both exact manifests passed No-op 0/N and Reference N/N controls
(N=4 and N=12). Scorer and provenance self-tests passed.
Only 1/48 calls truncated, compared descriptively with 22/48 in the archived
4096-token condition. This supports feasibility of this higher-budget condition,
but changed runtime/date and a nonrandomized historical comparison prevent
attributing all differences to output budget alone.

The constraint Baseline/Full paired contract outcomes have four
Baseline-only successes and zero Full-only successes; eight task outcomes
agree. Baseline/Minimal has three Baseline-only and one Minimal-only success.
These are small task samples, one deterministic call per condition, not
independent replicated effects. Dependency-mirror primary endpoint is tied
at zero, so the preregistered two-manifest directional gate is not met.

Semantic success and format compliance are distinct: neither replaces the
preregistered contract-success endpoint. Do not relax the parser to raise scores.
No rule ablation is justified by this experiment.

The source archive has no Git checkout: git_sha/git_dirty in generation/scoring
metadata are null. Source identity is supplied by the tracked run's immutable
commit, not by those null fields. Input/scorer/oracle/parser hash validation
is verified; this does not imply complete model-build or runtime reproducibility.
Quantization is recorded as 4bit; model artifact checksum and effective configured
context are not established. Historical partial attempts remain separate.

Next proposed work: inspect preserved per-task failure categories and prompt
information equivalence before designing another preregistered comparison.
Do not launch further compute automatically from these results.
