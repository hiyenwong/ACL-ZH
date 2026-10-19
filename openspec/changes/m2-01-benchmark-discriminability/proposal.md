# M2-01: Benchmark Discriminability Calibration

Status: proposed / NOT EXECUTED
Date: 2026-10-19
Owner: ACL-ZH research
Depends on: P2-01, P2-02 and P2-03 (completed)
Evidence baseline: commit 5d1e2d4a4cb37b1e235869dc3723a3932c085bcf

## Why

ACL-ZH has a functioning benchmark harness, but its current local experiments do not discriminate between prompt variants. The 4B model floors, the 12B model approaches a ceiling on the edit-content diagnostic track, and the forced-reasoning 8B model exhausted its completion budget on 22/48 runs. Additional runs on these same conditions would not answer whether controlled Chinese helps agents.

## What changes

- Add a PRE-REGISTERED model/task calibration phase, completely separated from the confirmatory evaluation.
- Use separate calibration and locked evaluation task sets; never select confirmatory tasks using variant performance.
- Verify no-op/reference controls and provenance before any scored run.
- Track truncation, contract compliance, semantic success, and task success separately.
- Define a fail-closed GO / NO-GO / INCONCLUSIVE decision for proceeding to M2-02.
- Provide a local LM Studio execution plan without claiming a model run has occurred.

## Scope

IN: edit-content calibration workflow and guardrails; later a separately versioned autonomous-agent protocol.
OUT: changing historical prompts, parser, scorer, hidden oracle, or previously published results; changing the v0.1 edit-content contract; claiming ACL effectiveness; executing M2-02; claiming an OpenSpec CLI validation run.

## Deliverables

1. This OpenSpec change (proposal, design, tasks, delta spec).
2. A calibration task manifest / held-out evaluation manifest with documented provenance and non-overlap (implementation task).
3. A frozen calibration experiment JSON and executable local runbook (implementation task).
4. Calibration raw traces, scoring, report and gate decision after the user runs LM Studio (execution task).

## Success criteria

A calibration run reaches a documented, non-floor/non-ceiling operating regime on held-out, non-variant-selected tasks, with no major truncation or protocol failure. This is an EXPERIMENT READINESS result, not evidence that ACL-ZH improves success. Any inconclusive outcome is recorded without post-hoc rule changes.

## Risks and mitigations

- Selection bias: use calibration-only natural-language/reference probes; evaluation tasks held out.
- Leakage: hash/task-family overlap checks; use a disjoint task set when feasible; disclose related templates.
- Forced reasoning: preflight on non-benchmark toy tasks; freeze budgets before scored calls.
- Runtime limitations: label edit-content results diagnostic; never pool with coding-agent CLI outcomes.
- Small sample: use calibration thresholds for feasibility only; do not claim statistical significance.
