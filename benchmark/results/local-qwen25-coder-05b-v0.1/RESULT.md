# Qwen2.5-Coder-0.5B real-model smoke result

Experiment: `local-qwen25-coder-05b-smoke-v0.1-parallel`

Workflow run: 37908944302

Model: `Qwen/Qwen2.5-Coder-0.5B-Instruct`

Track: `local-open-model`

Runs: 18 = 6 tasks × 3 prompt variants × 1 repetition.

## Result

| Variant | n | Task success | Hidden oracle | Patch apply |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 6 | 0/6 | 0/6 | 0/6 |
| Minimal ACL | 6 | 0/6 | 0/6 | 0/6 |
| Full ACL | 6 | 0/6 | 0/6 | 0/6 |

## Interpretation

This is a real-model result, but it is **not evidence that ACL-ZH has no effect**.

The model exhibited a floor effect before behavioral correctness could be measured: none of the 18 first-shot responses produced a patch accepted by `git apply`.

Manual inspection found repeated response-format failures, including Markdown code fences around diffs, malformed hunk headers, fabricated index metadata, patches against incorrect file contents, and unchanged or incomplete code.

Because Baseline, Minimal ACL, and Full ACL are all at the measurement floor, this model is not suitable for estimating the treatment effect of controlled-language structure on the current task set.

## Decision

Do not use this run to support a positive or negative ACL-ZH performance claim.

Escalate to a stronger fixed open coding model and retain this run as a documented lower-capability boundary condition.
