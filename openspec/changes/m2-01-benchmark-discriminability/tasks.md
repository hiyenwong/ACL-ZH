# Implementation & Local Execution Tasks — M2-01

Status: pilot implementation committed; new model experiment NOT EXECUTED; CI not independently verified.

## Specification and review
- [x] T1. Draft M2-01 proposal, design, requirements and gates.
- [ ] T1a. Human/code review, resolve conflicts with existing experiment conventions, approve protocol before building manifests.

## Implementation (repository changes required)
- [ ] T2. Build independent calibration and held-out evaluation task manifests; document fixture/oracle provenance, family distribution and split leakage audit. **Partial:** 12 historical constraint tasks copied into baseline-only pilot; these are NOT independent or held-out.
- [ ] T3. Implement deterministic split/manifest validation and both-manifest no-op/reference control assertions in CI. **Partial:** pilot manifest/experiment validator, exact-manifest controls and CI workflow committed; independent split and evaluation manifest still pending.
- [x] T4 (pilot scope only). Reuse original edit-content runner/scorer unchanged; wrapper pins decoding and checks clean worktree, fresh exact-manifest no-op/reference controls; report categorizes success, format, semantic and finish_reason truncation. Broader multi-family matrix deferred.
- [ ] T5. Add `benchmark/calibration/experiments/` pinned experiment JSON, a reproducible runbook with VERIFIED CLI syntax, a machine-checkable report schema, and prospective M2-02 analysis preregistration. **Partial:** committed model-template + prepare script, local runbook, report JSON generator. Exact model pinning requires local inventory and a NEW pre-inference commit. Held-out M2-02 preregistration pending.
- [ ] T6. Run local self-tests and CI, inspect diffs and freeze SHA hashes in committed preregistration before any scored generation. **Not yet verified:** GitHub CLI checkout not possible in current execution environment; CI workflow submitted but execution result not verified.

## Local LM Studio execution (user machine)
- [ ] T7. Pull fixed commit; capture model inventory and runtime/hardware metadata.
- [ ] T8. Run non-benchmark toy preflight, choose model and token budget by declared rules, then commit model-condition amendment BEFORE calibration scoring.
- [ ] T9. Run baseline-only calibration task×model matrix, stateless requests, immutable first responses and exact provenance.
- [ ] T10. Score and review raw results; verify finish_reason, generation/scoring hashes and controls with fail-closed behavior.
- [ ] T11. Write and commit calibration report with explicit GO / NO-GO / INCONCLUSIVE, unsuccessful conditions included.

## Post-calibration decision
- [ ] T12. If GO, create a NEW OpenSpec change M2-02 and lock confirmatory baseline/minimal/full held-out A/B/C experiment before inference.
- [ ] T13. If NO-GO/INCONCLUSIVE, document root cause and preregister a new task/model calibration version. No silent task mutation.

## Acceptance (ALL required for M2-01 completion)
- A1: the chosen experiment condition and manifests are committed before scored inference; all provenance verified, no overrides.
- A2: no-op/reference controls match expected 0/N and N/N on each manifest, no oracle bypass or manifest/score version mismatch.
- A3: calibration and evaluation partitions are independent according to documented leakage audit; held-out outcomes never used for selection.
- A4: raw first responses, complete run counts, truncation rates and score breakdown are preserved, linked and reproducible.
- A5: outcome is labeled GO, NO-GO or INCONCLUSIVE according to frozen criteria, with negative results retained.
- A6: report explicitly does not claim ACL-ZH effectiveness from calibration and never mixes strict-diff, edit-content or autonomous-agent outcomes.

## Current handoff (2026-10-19)

Pilot sources: `benchmark/calibration/RUNBOOK.md`. The 12-task pilot may be run locally after a real model condition is pinned and committed. Its output can at most support readiness assessment; it is not confirmatory evidence. M2-01 acceptance is NOT met until independent task split, CI verification, local results and documented gate are complete.
