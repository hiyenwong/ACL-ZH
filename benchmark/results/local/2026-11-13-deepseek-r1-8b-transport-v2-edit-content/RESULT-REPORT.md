# Explicit response transport v2: completed result

Run: a52f5cf4-8c79-4cf3-825c-1e0b145ec0da. Commit: b584045.
All 48 raw responses preserved. Same 8B model, 16384 output-token budget,
task instructions, task order, frozen parser/oracle and contract v0.1.
Only the shared prompt wrapper changed. Prior scores remain immutable.

## Interpretation

The response-format bottleneck is substantially reduced in this observed
condition. This is an exploratory historical comparison of a bundled wrapper
change, not a randomized component-level causal demonstration.
There is no preregistered cross-manifest language-variant separation:
dependency-mirror contract success is tied at 1/4 per variant; constraint
Minimal is 11/12, Baseline 10/12, Full 9/12. No efficacy/harm claim,
significance claim or rule ablation is supported by these small samples.

## dependency-mirror

| Variant | Contract success old → new | Semantic success old → new | Format compliance old → new | n |
|---|---|---|---|---:|
| baseline | 0 → 1 | 1 → 1 | 0 → 4 | 4 |
| minimal | 0 → 1 | 3 → 1 | 0 → 4 | 4 |
| full | 0 → 1 | 1 → 1 | 2 → 4 | 4 |

| Task | Baseline | Minimal | Full |
|---|---|---|---|
| dependency-anchor-01 | fail | fail | pass |
| dependency-verbose-01 | pass | pass | fail |
| dependency-no-target-file-01 | fail | fail | fail |
| dependency-no-file-ban-01 | fail | fail | fail |

Truncated calls: []

[Raw scoring aggregate](dependency-mirror/aggregate-edit-content.json); [Generation metadata](dependency-mirror/generation-metadata.json).

## constraint

| Variant | Contract success old → new | Semantic success old → new | Format compliance old → new | n |
|---|---|---|---|---:|
| baseline | 8 → 10 | 9 → 10 | 8 → 12 | 12 |
| minimal | 6 → 11 | 9 → 11 | 6 → 12 | 12 |
| full | 4 → 9 | 6 → 9 | 5 → 9 | 12 |

| Task | Baseline | Minimal | Full |
|---|---|---|---|
| constraint-schema-01 | pass | pass | pass |
| constraint-path-01 | pass | pass | pass |
| constraint-immutable-01 | pass | pass | fail |
| constraint-side-effect-01 | pass | pass | pass |
| constraint-stdlib-01 | pass | pass | pass |
| constraint-retry-01 | fail | pass | fail |
| scope-01 | pass | pass | pass |
| constraint-api-01 | pass | pass | pass |
| compatibility-01 | pass | pass | pass |
| dependency-01 | fail | fail | pass |
| constraint-return-01 | pass | pass | fail |
| exception-01 | pass | pass | pass |

Truncated calls: [('constraint-immutable-01', 'full'), ('constraint-retry-01', 'full'), ('constraint-return-01', 'full')]

[Raw scoring aggregate](constraint/aggregate-edit-content.json); [Generation metadata](constraint/generation-metadata.json).

## Remaining blockers and next decision

Dependency-mirror: all 12 responses now comply with the format, but only
3/12 pass semantics; failure has shifted toward actual task implementation.
Minimal semantic success falls from 3/4 to 1/4 despite improved formatting:
the wrapper adjustment is not a uniform semantic improvement.
Constraint: all Baseline/Minimal responses comply. All three noncompliant
Full responses are also truncated (immutable, retry, return). Budget
exhaustion remains a local Full-condition failure mode, not proof that
longer ACL causes truncation generally. Total truncation is 3/48 versus
1/48 in the parent condition. Do not fix scores by lenient parsing.

Next: retain transport v2 as a useful candidate for future protocol design,
but audit task-information equivalence and inspect remaining semantic misses
before another confirmatory language study. Avoid further wrapper tuning on
this same test set as evidence of generalization. No new compute launched.

## Validation and reproducibility boundary

No-op 0/4 and 0/12, Reference 4/4 and 12/12; scorer/provenance and
wrapper instruction/source-preservation self-tests passed. Scoring hashes
verified without overrides. Source archive Git fields are null; source
identity comes from the tracked run commit b584045. Exact model build checksum
and effective context remain unverified. The endpoint is local; scores are
diagnostic edit-content outcomes, not autonomous-agent or strict-diff scores.
