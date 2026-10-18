# Post-Remediation Review: Edit-Content Benchmark

Review ID: `post-remediation-review-edit-content-v0.1`  
Date: 2026-10-18  
Reviewed commit: `a75b6bceabdf764dda28fc8f550d9809d653bfa0`  
Status: **ACCEPTED WITH FOLLOW-UP ITEMS**  
Scope: benchmark correctness, historical re-scoring, README evidence claims, LM Studio reproducibility metadata

## 1. Executive conclusion

The P1 edit-content scoring remediation is accepted.

The reviewed update fixes the previously identified contract-scoring defect without changing the frozen parser, hidden oracle, prompts, or historical raw model responses.

The previous local positive signal:

`Full ACL format compliance 4/4 vs Baseline/Minimal 1/4`

is no longer supported after strict contract re-scoring. The corrected result is:

`0/4 vs 0/4 vs 0/4`

for format compliance on the gemma-3-4b dependency-mirror edit-content run.

Therefore the previous format-compliance variant signal was a measurement artifact and has been correctly removed from README-level conclusions.

At the time of this review, the repository does **not** contain a validated local Baseline / Minimal ACL / Full ACL performance separation.

This review does not validate ACL-ZH effectiveness.

---

## 2. Accepted remediation items

### A1 — Markdown fence detection

Accepted.

The scorer now treats Markdown fence lines beginning with:

- ````
- `~~~`

inside a parsed FILE block as edit-content contract violations.

This closes the defect that caused fence-wrapped file content to be counted as format compliant.

### A2 — Duplicate file-path detection

Accepted.

Multiple FILE blocks targeting the same path are now classified as a format violation.

### A3 — Semantic success and contract success separation

Accepted.

The metrics are now explicitly defined as:

```text
semantic_task_success =
    visible_tests_pass
    AND hidden_oracle_pass
    AND NOT constraint_violation

task_success =
    semantic_task_success
    AND format_compliant
```

This distinction is required because semantic task-solving and response-contract compliance are different measurements.

### A4 — Frozen parser preserved

Accepted.

The remediation does not loosen `benchmark/local-model/edit_content_parser.py`.

Contract validation is implemented outside the frozen parser.

### A5 — Regression tests

Accepted.

The self-test now covers:

- valid contract response;
- empty response;
- unified-diff response;
- forbidden/disallowed path;
- backtick fenced content;
- tilde fenced content;
- interior fence;
- residual prose;
- duplicate file path;
- semantic success with contract failure.

This is materially stronger than the previous scorer self-test.

### A6 — Historical re-scoring

Accepted.

The three committed edit-content runs were re-scored from existing raw responses.

Reviewed result families:

- gemma-3-4b dependency-mirror edit-content;
- gemma-4-12b dependency-mirror edit-content;
- gemma-4-12b constraint-focused edit-content.

No replacement model generations were required for this remediation.

### A7 — README evidence correction

Accepted.

The repository now explicitly records that the former gemma-3-4b format-compliance advantage was caused by scorer under-detection of contract violations.

The repository no longer presents that result as a variant signal.

### A8 — 7B statement downgraded

Accepted.

The current evidence supports only an experiment-selection hypothesis:

> The existing 4B and 12B local capability points suggest that an intermediate capability region may be more discriminating for the current task set. A model around the 7B class is a reasonable next test point, not a validated threshold.

The repository must not describe 7B as a proven capability boundary.

### A9 — LM Studio metadata hardening

Accepted.

The local runner now records or accepts explicit metadata for:

- git SHA;
- UTC run timestamp;
- LM Studio / `lms` version;
- quantization;
- context length;
- hardware note;
- RAM;
- reasoning effort;
- exporter;
- experiment;
- manifest;
- decoding parameters.

Unknown values are recorded rather than guessed.

---

## 3. Corrected evidence state

Current local evidence must be interpreted by track.

### 3.1 Strict unified-diff track

Recorded count: **150 generations**

This track measures both:

- task-solving ability;
- strict unified-diff serialization compliance.

A patch serialization floor can therefore hide correct edit intent.

### 3.2 Edit-content diagnostic track

Recorded count: **60 generations**

This track is diagnostic and remains separate from strict unified-diff results.

It must not be merged into strict task-success totals.

### 3.3 Current observable variant separation

After the 2026-10-15 remediation:

**No validated local variant separation remains.**

The current repository evidence does not support:

- Full ACL task-success advantage;
- Minimal ACL task-success advantage;
- constraint-family superiority;
- a validated model-size threshold;
- general ACL-ZH effectiveness.

---

## 4. Remaining P2 follow-up items

These are not blockers for accepting commit `a75b6bce`, but they should be completed before treating the local benchmark as publication-grade.

### P2-1 — Bind result records to scorer/oracle/manifest versions

Current local metadata records the repository git SHA, which is useful but coarse.

A future re-score can change if any of the following change:

- task manifest;
- hidden oracle implementation;
- scorer implementation;
- experiment definition.

Add immutable content hashes to scored result metadata.

Minimum recommended fields:

```text
experiment_sha256
manifest_sha256
scorer_sha256
oracle_source_sha256
parser_sha256
```

For strict-diff scoring also record the relevant strict scorer source hash.

For edit-content scoring record the frozen parser hash separately.

Purpose:

- distinguish generation-time state from scoring-time state;
- make historical re-scoring auditable;
- detect accidental scoring-definition drift.

### P2-2 — Define the boundary of Markdown-fence detection explicitly

The current rule classifies any FILE-content line whose left-stripped text begins with:

- ````
- `~~~`

as a format violation.

This matches the current response contract, but the exact boundary should be documented as a **contract rule**, not left only as scorer implementation behavior.

Reason:

A future benchmark task could legitimately require source text containing a Markdown-fence-looking line. If that occurs, the current contract and task domain would conflict.

Required action before such tasks are introduced:

1. define whether fence-like source content is outside the edit-content track's supported task domain; or
2. version the response contract and parser/scorer together.

Do not silently loosen the current frozen contract after seeing model output.

This is a prospective design risk, not a confirmed defect in the current task set.

### P2-3 — Add a scored-result provenance block

Each aggregate/report should include a provenance section containing at least:

```text
generation_git_sha
scoring_git_sha
raw_response_set_sha256
experiment_sha256
manifest_sha256
scorer_sha256
oracle_source_sha256
parser_sha256
```

The raw response set hash should be computed deterministically from:

- relative response path;
- response bytes;

in stable sorted order.

### P2-4 — Do not launch the next large model sweep before provenance locking

Before the next 7B-class or harder-task experiment:

1. implement content-hash provenance;
2. self-test it;
3. document the result schema;
4. freeze the next experiment config and task manifest;
5. then run the next model condition.

This reduces the chance of collecting another large result set whose exact scoring definition is difficult to reconstruct later.

---

## 5. Validation state

Reviewed GitHub Actions for commit `a75b6bceabdf`:

- Benchmark self-test: **SUCCESS**
- Local open-model benchmark: **SUCCESS**
- Parallel local open-model benchmark: **SUCCESS**

The P1 remediation therefore passes both code-level review and current CI validation.

CI success validates the implemented harness behavior. It does not validate ACL-ZH effectiveness.

---

## 6. Research interpretation after remediation

The strongest defensible conclusions are currently:

1. strict unified-diff serialization can dominate measured failure for some local models;
2. the edit-content diagnostic track can separate serialization failure from semantic task-solving;
3. gemma-4-12b saturates the current dependency-mirror edit-content task family and nearly saturates the current constraint-focused task family;
4. gemma-3-4b does not solve the dependency-mirror edit-content task family under the frozen contract;
5. after correcting the scorer, none of the tested local conditions show a validated Baseline / Minimal ACL / Full ACL separation.

The following remain hypotheses:

- an intermediate-capability model may provide better discrimination;
- harder tasks may reduce the 12B ceiling effect;
- some ACL-ZH rule family may help near a model capability boundary.

These hypotheses require new, prospectively frozen experiments.

---

## 7. Next required task

Before the next model experiment, create a dedicated provenance-hardening task.

Recommended task ID:

`benchmark-result-provenance-v0.1`

Required deliverables:

- content hashes for experiment, manifest, scorer, oracle and parser;
- deterministic raw-response-set hash;
- aggregate provenance block;
- self-test covering hash stability and change detection;
- documentation of generation-time vs scoring-time provenance;
- no change to existing benchmark semantics.

Only after that task passes should the project proceed to the next discriminating model experiment.

---

## 8. Acceptance decision

Decision: **ACCEPT P1 REMEDIATION**

Accepted commit:

`a75b6bceabdf764dda28fc8f550d9809d653bfa0`

Remaining work:

- P2 provenance locking;
- explicit response-contract domain documentation;
- next experiment only after provenance hardening.

Evidence boundary:

This review accepts benchmark correctness improvements only. It does not establish that ACL-ZH improves coding agents.
