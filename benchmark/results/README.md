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

This validates the basic scorer behavior, not ACL-ZH itself. After the runner was hardened to move prompt files outside the workspace and detect untracked files, the self-test caught a reference-harness regression. The interface was fixed and the latest scorer self-test returned to PASS.

## Agent benchmark

Status: **not yet executed**

No task-success, constraint-violation, or token-efficiency claim for ACL-ZH is currently supported.

The next publishable result must contain Baseline, Minimal ACL, and Full ACL runs under the same model/environment controls.

## Local LM Studio runs

Diagnostic-grade local runs (LM Studio, deterministic decoding). Each directory has a RESULT-REPORT.md with the full environment record and evidence boundary. Edit-content rows are a separate diagnostic track and are never merged with strict unified-diff counts.

| Date | Model | Manifest | Track | Result |
| --- | --- | --- | --- | --- |
| 2026-10-11 | gemma-3-4b @4bit | dependency-mirror v0.4 | strict diff | 0/12 (serialization + semantic floor) |
| 2026-10-11 | gemma-4-12b-qat @q4_0 | dependency-mirror v0.4 | strict diff | 0/12 patch apply; edit content 12/12 correct on post-hoc inspection |
| 2026-10-14 | gemma-4-12b-qat @q4_0 | dependency-mirror v0.4 | edit-content | 12/12, all variants saturated |
| 2026-10-14 | gemma-3-4b @4bit | dependency-mirror v0.4 | edit-content | 0/12; format compliance 0/12 after remediation (re-scored 2026-10-15: all parsed blocks wrap content in fences — contract violations); no variant signal |
| 2026-10-14 | gemma-4-12b-qat @q4_0 | constraint v0.3 | edit-content | 33/36; constraint-return-01 fails in all variants; no variant separation |
| 2026-10-19 | deepseek-r1-0528-qwen3-8b @4bit | dependency-mirror v0.4 | edit-content | 0/12 floor; no variant signal |
| 2026-10-19 | deepseek-r1-0528-qwen3-8b @4bit | constraint v0.3 | edit-content | 1/36 (minimal, constraint-side-effect-01); 19/36 truncation; single-manifest single-task observation labeled exploratory per prereg |

All edit-content results above are scored under `edit-content-contract-v0.1` (strict fence prohibition; see `benchmark/local-model/EDIT-CONTENT-CONTRACT.md`). Aggregates carry `contract_version` plus a provenance block identifying the exact scorer/oracle/parser hashes.

Harness note: during these runs a latent defect was found and fixed — the v0.4 mirror task ids had no hidden-oracle branch (always False) and no No-op/Reference control. Fixed in `f0693a6`; controls now pass (0/4 and 4/4) and no recorded result was affected.

Scorer remediation (2026-10-15): the edit-content scorer's `format_compliant` previously missed contract violations — Markdown fence lines (``` or ~~~) inside block content and duplicate file paths. The scorer now detects both (frozen parser unchanged), and distinguishes `semantic_task_success` (tests + oracle + no constraint violation) from `task_success` (semantic + format compliant). All three edit-content runs were re-scored from their unchanged raw responses (response SHAs, run manifests, and generation metadata verified invariant). The gemma-3-4b "Full ACL format compliance 4/4 vs 1/4" claim did not survive re-scoring (0/4 vs 0/4) and has been removed; the two gemma-4-12b runs are unchanged.

Preregistered 8B experiment (2026-10-19, PREREG-NEXT-DISCRIMINATING-V0.1 + Amendment A1): `deepseek/deepseek-r1-0528-qwen3-8b` (4bit, ctx 131072) ran both edit-content manifests with generation-time provenance and fail-closed verified scoring (no overrides). Amendment A1 pinned max_tokens 4096 + reasoning_effort none for this forced-reasoning model (cross-model decoding caveat vs the 256-token 4B/12B runs). Even so, 22/48 runs exhausted the token budget on reasoning tokens (`finish_reason: length`, mostly empty content): the dependency-mirror run is a complete floor (0/12, no variant signal), and the constraint run is near-floor (1/36; the single Minimal success on constraint-side-effect-01 is a single-manifest single-task observation, labeled exploratory per the preregistered both-manifests rule). The 8B condition was chosen as the available intermediate point; it is not a validated capability threshold.

## Publication rule

README claims must point to a committed result or a reproducible CI run. Predictions and intuitions must remain labeled as hypotheses.
