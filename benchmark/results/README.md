# Benchmark Results

## Static v0.1

Status: **completed**

The initial 12-pair linguistic comparison found:

| Metric | Baseline | Full ACL |
| --- | ---: | ---: |
| Mean Chinese characters | 21.5 | 70.417 |
| Ambiguity-marker hits | 1.5 | 0 |
| Explicit sections | 0 | 2.167 |
| Flow markers | 0.083 | 0.917 |
| Normative markers | 0.083 | 0.75 |

Full ACL was approximately **3.28× longer**.

This demonstrates only that the rewrite changes measurable linguistic properties. It does not demonstrate better coding-agent performance.

## Harness self-test

Status: **completed / PASS**

GitHub Actions validates two controls:

| Control | Expected | Observed |
| --- | ---: | ---: |
| No-op agent | 0 / 6 success | 0 / 6 |
| Reference agent | 6 / 6 success | 6 / 6 |
| Aggregate smoke test | PASS | PASS |

This validates the basic scorer behavior, not ACL-ZH itself.

## Agent benchmark

Status: **not yet executed**

No task-success, constraint-violation, or token-efficiency claim for ACL-ZH is currently supported.

The next publishable result must contain Baseline, Minimal ACL, and Full ACL runs under the same model/environment controls.

## Publication rule

README claims must point to a committed result or a reproducible CI run. Predictions and intuitions must remain labeled as hypotheses.
