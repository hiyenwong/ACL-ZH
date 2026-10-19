# Benchmark Calibration — Delta Requirements

Status: proposed
Scope: Input Track, local edit-content diagnostic experiments

## ADDED Requirement: Calibration independence

The system SHALL keep calibration tasks and confirmatory evaluation tasks in disjoint named manifests with recorded immutable hashes. It SHALL validate exact duplicates and inspect near-duplicate fixture/oracle templates. The system MUST NOT use held-out Baseline/Minimal/Full outcomes to choose a model, rewrite tasks, or tune prompts.

### Scenario: task leaks across manifests
GIVEN a fixture and oracle occur in both manifests
WHEN the split audit runs
THEN the gate FAILS before inference and identifies the conflicting task IDs.

## ADDED Requirement: Preflight budget integrity

The system SHALL run non-benchmark toy preflight for a forced-reasoning candidate. It SHALL record response content, finish_reason, output/reasoning usage where reported, and whether decoding controls are honored. A token-budget change MUST be pinned and committed before a scored experiment.

### Scenario: response truncated
GIVEN finish_reason indicates length, or a required end marker is missing
WHEN result classification occurs
THEN the run is classified with truncation diagnostics and MUST NOT silently count as a normal semantic failure.

## ADDED Requirement: Fail-closed evidence

The system SHALL use immutable prompts, manifests, parser, oracle and scorer, with generation and scoring provenance hashes. A mismatch MUST stop promotion; override scores are diagnostic-only and MUST NOT satisfy acceptance.

### Scenario: scoring inputs changed
GIVEN a manifest SHA differs from its generation-time baseline
WHEN scoring begins
THEN it fails closed and the report identifies both hashes.

## ADDED Requirement: Model selection without variant bias

Calibration model selection SHALL inspect natural-language Baseline task success and protocol reliability only. The working success target is 20–80% on calibration tasks; integrity target is at least 95% non-truncated valid runs. These are feasibility gates, not statistical evidence. Minimal and Full scores SHALL remain unobserved during selection.

### Scenario: no candidate qualifies
GIVEN every candidate is at floor, ceiling, or fails integrity
WHEN calibration concludes
THEN the decision is NO-GO or INCONCLUSIVE with reasons, not a post-hoc relaxation of limits.

## ADDED Requirement: Distinct evidence tracks

The system SHALL keep strict unified-diff, edit-content diagnostic and autonomous coding-agent results distinct, with track metadata and separate aggregates.

### Scenario: combining diagnostic and agent results
GIVEN two runs belong to different tracks
WHEN an aggregate is requested
THEN a combined success-rate claim is rejected.

## ADDED Requirement: Auditable readiness decision

The system SHALL generate a report containing full task×model outcome rows, exclusions, controls, hashes, budget-related truncation, per-family success and a GO / NO-GO / INCONCLUSIVE outcome. A GO only authorizes a separately pre-registered M2-02 evaluation; it does not validate ACL-ZH.

### Scenario: calibrated model satisfies criteria
GIVEN controls pass, integrity reaches the frozen threshold and baseline success falls inside the feasibility window
WHEN calibration report is frozen
THEN it may state GO for M2-02 readiness, without an ACL effectiveness claim.
