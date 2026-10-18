# ACL-ZH — Post-remediation Review and Next Validation Plan

**Document ID:** ACLZH-BENCH-REVIEW-2026-10-18  
**Status:** Review accepted; follow-up tasks open (not yet implemented)  
**Reviewed commit:** `a75b6bceabdf764dda28fc8f550d9809d653bfa0`  
**Scope:** LM Studio edit-content diagnostic benchmark, reproducibility, and evidence publication  
**Priority:** P2 follow-up; no immediate new inference required

## 1. Objective

Record the technical acceptance of the 2026-10-15 benchmark-remediation commit, its remaining measurement/reproducibility risks, and executable acceptance criteria before the next local model experiment.

**This document is a review and task plan. It does not implement a scorer change, rerun a model, or promote a new research conclusion.**

## 2. Verified status and evidence boundary

- The remediation implements `semantic_task_success = visible_tests_pass AND hidden_oracle_pass AND NOT constraint_violation`.
- The edit-content `task_success` now additionally requires `format_compliant`.
- The scorer detects fenced block content (backtick and tilde fence prefixes), duplicate FILE paths, empty paths, residual prose, and disallowed paths; the frozen `edit_content_parser.py` is unchanged.
- The new self-test exercises valid output, fenced content, residual prose, duplicate paths, and semantic success with contract failure.
- The 2026-10-14 saved edit-content response sets were re-scored without replacing model outputs. Gemma 3 4B's earlier apparent format-compliance separation was withdrawn: Baseline 0/4, Minimal 0/4, Full 0/4. This corrects the earlier **4/4 vs 1/4** claim.
- Gemma 4 12B edit-content diagnostic results remain dependency mirror **12/12** and constraint-focused **33/36**, with **no observed variant separation**.
- README currently reports **150 strict-diff inference runs** and **60 edit-content diagnostic inference runs**, counted separately. These are run counts, not independent causal replications.
- The head-commit GitHub Actions **Benchmark self-test** run `38762916125` concluded **success**. A successful CI run does not prove the absence of untested logical errors.

**Research conclusion:** No reliable task-success benefit of ACL-ZH has been established. Do not merge the two benchmark tracks or call these counts evidence of effectiveness.

## 3. Follow-up work items

### P2-01 — Specify legal literal fence lines vs prohibited Markdown wrapping

**Observation:** `contains_markdown_fence(content)` currently rejects any line whose left-stripped text starts with three backticks or three tildes. This enforces the project's present strict contract but may reject legitimate source-file contents in languages or formats that intentionally contain such lines. **This is a potential contract-design ambiguity, not a confirmed current bug.**

**Task:**
1. Write explicit, language-neutral examples of prohibited Markdown wrapper fences and legitimately embedded source content.
2. Decide *prospectively* whether the frozen edit-content contract prohibits every fence-looking content line, or only fences serving as Markdown wrappers.
3. Add negative and positive tests for the chosen rule, including `~~~`, ```python`, fence-like literals inside strings, and blocks with multiple files.
4. If the policy changes the accepted output language, **version the contract and scorer** (e.g. v0.2); preserve v0.1 results and never silently reclassify them.
5. Label all results by the contract/scorer version.

**Acceptance:** The rule is documented before future inference, tests cover the selected interpretation, and previously published v0.1 counts remain traceable.

### P2-02 — Pin input, model and scorer provenance in each run

**Observation:** `run_lm_studio.py` now records git SHA, UTC timestamp, version (best effort), RAM, and explicit quantization/context length/hardware notes. The current edit-content scorer still takes the manifest and working-tree oracle/scorer as live inputs; this makes historical rescoring sensitive to later source revisions.

**Task:**
1. Add to newly generated run metadata: `experiment_sha256`, `manifest_sha256`, `exporter_sha256`, `scorer_sha256`, `oracle_sha256`, `parser_sha256`, `prompt_bundle_sha256`, and the repository HEAD plus a dirty-worktree flag (where available).
2. Define hashing over exact bytes and a stable prompt-bundle ordering; document the algorithm and missing-file behavior.
3. At scoring time, record actual hashes for the scorer, oracle and parser **used in that scoring pass**; compare manifest/prompt hashes against run metadata and fail closed, or explicitly require an auditable `--allow-version-mismatch` diagnostic override.
4. Make the override preserve both originally recorded and actual hashes and label the score as `rescore`; never overwrite archived scores without a versioned audit record.
5. Do not infer quantization or LM Studio context length from the model name. Unknown metadata must remain `null`/unknown.
6. Add a reproducibility self-test proving that a changed manifest or scorer is detected and that an unchanged bundle passes.

**Acceptance:** Re-scoring an archived run with changed inputs or scorer code is detectable and reported; original raw responses and earlier score files remain immutable.

### P2-03 — Lock experiment comparison and publication criteria

**Task:**
1. Treat `strict-diff` and `edit-content` as separate predefined outcomes.
2. Specify before inference: fixed model build/quantization, context window, temperature, top_p, seed/reasoning budget, fresh chat, exact manifest/scorer versions, run order, primary endpoint and failure categories.
3. Use paired task-level variant comparisons and report raw counts, per-task outcomes, and confidence/uncertainty rather than merely totals. Identical deterministic generations are not independent replications.
4. Consider a mid-capability model (such as ~7B) or more discriminating tasks **as hypotheses for experiment selection**, not as a proven model-size threshold.
5. Keep Baseline/Minimal/Full instruction facts matched in future confirmatory studies; separate added information from controlled-language structure.
6. Require No-op 0/N and Reference N/N controls for each new manifest before conducting scored inference.

**Acceptance:** A preregistered protocol exists before the next study; no claims of effectiveness arise from mere response formatting or a single task.

## 4. Hard constraints

- Do **not** alter frozen `benchmark/local-model/edit_content_parser.py` or hidden oracles to rescue model outputs.
- Do **not** modify, delete, repair, or regenerate archived raw responses.
- Do **not** silently change task manifests or prompts used for past evaluations.
- Do **not** treat Markdown-format compliance as task success.
- Do **not** mix strict unified-diff results with edit-content diagnostic results.
- Do **not** declare ACL-ZH validated from current evidence.
- Any intentionally changed contract requires a new version, dedicated tests, and a documented boundary from old results.

## 5. Validation checklist for a future implementation

- [ ] Versioned contract with clear examples and explicit fence semantics.
- [ ] Scorer unit tests and end-to-end self-test pass.
- [ ] Provenance hashes and dirty-worktree state captured reliably.
- [ ] Hash mismatch is detected before scoring; override produces an audit trail.
- [ ] Existing raw outputs and historical score files remain byte-identical.
- [ ] No-op/Reference controls pass for every newly used manifest.
- [ ] `python -m py_compile` for touched Python modules passes.
- [ ] GitHub Actions Benchmark self-test passes on implementation commit.
- [ ] README updates contain only evidence-backed, track-specific claims.
- [ ] Final report includes changed paths, version/hash table, before/after test matrix, CI run URL, commit SHA, and unresolved items.

## 6. Stop rules

Stop work and report a blocker instead of changing the evaluation definition if:
- preserved raw data cannot be verified;
- the change would require post-hoc parser leniency to raise prior scores;
- a hidden oracle must be modified to fit a model answer;
- historical experiment inputs cannot be unambiguously identified;
- a scorer-version mismatch would otherwise be silently accepted.

## 7. Suggested execution order

1. P2-02 provenance and hash-locking (before any further local experiments).
2. P2-01 explicit fence semantics and versioning decision.
3. P2-03 preregistration of the next discriminating experiment.
4. Review/commit the implementation and run CI, then execute any new LM Studio experiments.

**Completion output:** State implemented vs pending items explicitly; attach commits and CI evidence. This review commit does not satisfy these future implementation acceptance criteria.
