# Qwen2.5-Coder-1.5B post-hoc semantic audit

Source workflow: `37910311745`

Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct`

Status: **exploratory / post-hoc / not confirmatory**

The preregistered semantic parser required `<<<FILE:path>>>` markers. The model instead consistently emitted explicit file blocks such as `<<<src/names.py>>>` followed by fenced Python code.

A conservative post-hoc audit therefore extracted only blocks with an explicit path header followed by a fenced code block. It did not repair, rewrite, infer, or otherwise modify model code.

| Variant | Parse | Hidden oracle | Visible tests | Task success |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 5/6 (83.3%) | 2/6 (33.3%) | 5/6 (83.3%) | 2/6 (33.3%) |
| Minimal ACL | 6/6 (100%) | 4/6 (66.7%) | 5/6 (83.3%) | 3/6 (50.0%) |
| Full ACL | 6/6 (100%) | 5/6 (83.3%) | 5/6 (83.3%) | 4/6 (66.7%) |

## Task-level hidden-oracle results

- Baseline passed: `flow-01`, `validation-01`.
- Minimal ACL passed: `scope-01`, `multi-action-01`, `flow-01`, `validation-01`.
- Full ACL passed: `scope-01`, `multi-action-01`, `flow-01`, `validation-01`, `dependency-01`.
- `reference-01` failed in all three variants.

The `multi-action-01` model code passed the hidden behavioral oracle in Minimal and Full, but the model-generated test file contained invalid Python syntax, so end-to-end task success remained false.

## What this means

This is the first real-model run showing a monotonic signal consistent with the ACL-ZH hypothesis.

It is **not** evidence that ACL-ZH is proven effective.

Two major confounds remain:

1. the lenient extraction rule was introduced after inspecting model output;
2. Baseline, Minimal ACL, and Full ACL are not guaranteed to contain exactly the same task facts.

The next confirmatory experiment must freeze the parser before execution and compare information-matched prompt arms.
