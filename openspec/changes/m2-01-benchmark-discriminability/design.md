# Technical Design — M2-01

Status: proposed / not run

## Evidence and constraints

Existing project uses local-model/run_lm_studio.py, the frozen edit-content parser, local score_edit_content_run.py, hidden oracle, and generation/scoring provenance. Continue using these unless a separately reviewed change is necessary. Keep all historical results immutable.

## Phase 0: inventory and feasibility

1. Inventory LM Studio served models and exact identifier, quantization, context length, runtime version, hardware and availability.
2. Preflight each candidate with non-benchmark toy editing requests. Record separate response content, reasoning token usage where available, finish_reason, latency and token counts. Test whether reasoning_effort is actually honored.
3. Exclude a candidate when it repeatedly cannot emit a nonempty, complete response within the explicitly budgeted token limit. Record exclusions, not silent substitutions.
4. Do not assume the intermediate model size or nominal parameter count implies an operating point.

## Phase 1: calibration set design

- Create `benchmark/calibration/manifests/calibration-v0.1.jsonl` plus a machine-checkable set ID/hash and task-family metadata. Start with at least 12 independent calibration tasks; include dependency, constraint and realistic file-edit families. Exact count must be frozen before inference.
- Create separate `benchmark/calibration/manifests/evaluation-holdout-v0.1.jsonl` for M2-02 (target 30–50 independent tasks, final count set by a prospective precision/power plan). Do not inspect scored variant outcomes on this set during calibration.
- Ensure no identical fixture+oracle or trivially renamed duplicate crosses the split. Audit template and near-duplicate leakage; record limitations.
- Every task must have expected writable paths, forbidden paths, explicit success oracle, and no-op 0 / reference 1 controls. Verify aggregate control coverage on both manifest versions before use.
- Freeze manifest bytes, prompt exporter, parser, scorer, oracle, prompts and experiment JSON; publish SHA-256 hashes before scored inference.

## Phase 2: model and task difficulty calibration

Calibration selection may inspect ONLY baseline (natural-Chinese) task success and protocol integrity on the calibration set. Do not inspect Minimal or Full ACL outcomes until model/task selection and held-out evaluation are frozen. Do not rewrite tasks to favor any variant.

Working feasibility target: baseline success between 20% and 80% on calibration tasks, with enough successes and failures to differentiate difficulty. This is a planning heuristic, NOT a significance threshold. Require completion integrity (at least 95% non-truncated valid runs) and disclose format compliance separately. If no candidate meets these targets, declare NO-GO/INCONCLUSIVE and redesign in a NEW preregistered version; do not silently relax thresholds.

Choose at most one primary model/runtime condition for M2-02 before looking at held-out variant results. Other models may be prespecified as replication strata, never pooled implicitly.

## Phase 3: freeze confirmatory protocol

Before any held-out evaluation run:
- pin the selected model/build, quantization, hardware, runtime, context, decoding, maximum output tokens, tool permissions, prompt source and run order in committed experiment JSON;
- pin a primary task-level paired estimand (Minimal vs Baseline, Full vs Baseline), secondary endpoints and missing/truncated-data handling;
- adopt randomized/counterbalanced task×variant order, stateless fresh requests and independent task unit of analysis; deterministic repeats are not independent samples;
- preregister statistical approach: report matched discordant pairs, effect in percentage points with uncertainty intervals, and a multiplicity plan for two primary contrasts; never interpret exploratory differences as confirmatory;
- separate protocol compliance, semantic correctness and final task success;
- retain negative and inconclusive results with no result-dependent changes.

## Local execution handoff

From a clean checkout on the committed ref, inspect existing help and manifests:

```bash
git pull --ff-only
python benchmark/local-model/run_lm_studio.py --help
python benchmark/local-model/score_edit_content_run.py --help
curl http://127.0.0.1:1234/v1/models
```

The commands above are PREPARATION ONLY. M2-01-specific manifest and experiment JSON do not yet exist: implement tasks T2–T5 and review their hashes before giving a runnable scored command. Reuse the existing exporter/runner/scorer interface; do not invent command flags or paths. Do not score a partial run as though it were complete.

## Gate/report contract

Result report MUST contain:
- manifest/task split hashes, git SHA and clean-worktree status;
- precise model/runtime configuration and local preflight decision;
- control counts, raw response counts and score provenance;
- baseline successes/failures and breakdown per task family;
- truncations, contract violations, semantic failures and constraints separately;
- inclusion/exclusion decisions plus the exact threshold rule;
- decision `GO`, `NO-GO` or `INCONCLUSIVE` and reason;
- explicit statement: calibration is not evidence of ACL-ZH effectiveness.

No main-README effectiveness claim can be made from calibration alone.
