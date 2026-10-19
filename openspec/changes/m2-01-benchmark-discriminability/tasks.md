# Implementation & Local Execution Tasks — M2-01

Status: OpenSpec drafted; no new experiment executed.

## Specification and review
- [x] T1. Draft M2-01 proposal, design, requirements and gates.
- [ ] T1a. Human/code review, resolve conflicts with existing experiment conventions, approve protocol before building manifests.

## Implementation (repository changes required)
- [ ] T2. Build independent calibration and held-out evaluation task manifests; document fixture/oracle provenance, family distribution and split leakage audit.
- [ ] T3. Implement deterministic split/manifest validation and both-manifest no-op/reference control assertions in CI.
- [ ] T4. Implement or reuse calibration runner/exporter/score reporting without changing historical scoring semantics; add finish_reason/reasoning truncation diagnostics and per-family outcome matrix.
- [ ] T5. Add `benchmark/calibration/experiments/` pinned experiment JSON, a reproducible runbook with VERIFIED CLI syntax, a machine-checkable report schema, and prospective M2-02 analysis preregistration.
- [ ] T6. Run local self-tests and CI, inspect diffs and freeze SHA hashes in committed preregistration before any scored generation.

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
