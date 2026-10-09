# Qwen2.5-Coder-1.5B real-model smoke result

Experiment: `local-qwen25-coder-15b-smoke-v0.1`

Workflow run: 37909473050

Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct`

Track: `local-open-model`

Runs: 18 = 6 tasks × 3 prompt variants × 1 repetition.

## Result

| Variant | n | Task success | Hidden oracle | Patch apply |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 6 | 0/6 | 0/6 | 0/6 |
| Minimal ACL | 6 | 0/6 | 0/6 | 0/6 |
| Full ACL | 6 | 0/6 | 0/6 | 0/6 |

## Interpretation

This independently reproduces the floor effect observed with Qwen2.5-Coder-0.5B.

The measurement collapses before semantic task correctness can be observed because no first-shot response is accepted by `git apply`.

The current raw-unified-diff response contract therefore confounds output-format compliance with instruction comprehension and coding correctness.

## Decision

Do not interpret the all-zero result as evidence for or against ACL-ZH.

Before spending more model compute, split the benchmark into:

1. response-format compliance; and
2. semantic task correctness after a simpler deterministic file-replacement protocol.

Keep the original strict-diff experiment as a documented protocol-compliance benchmark.
