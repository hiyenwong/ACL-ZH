# Review Follow-up: Post-Remediation Benchmark Hardening

Review ID: `post-remediation-hardening-v0.2`  
Date: 2026-10-18  
Reviewed commit: `a75b6bceabdf764dda28fc8f550d9809d653bfa0`  
Status: **accepted with follow-up hardening items**  
Priority: **P2 — reproducibility and measurement integrity**

## 1. Review conclusion

The edit-content scoring remediation is accepted.

The following items are verified as corrected:

- Markdown-fence content is no longer counted as format-compliant.
- Duplicate FILE paths are treated as format violations.
- `semantic_task_success` and contract-level `task_success` are separated.
- `task_success = semantic_task_success AND format_compliant`.
- The frozen edit-content parser was not loosened.
- Historical edit-content runs were re-scored from preserved raw responses.
- The previously reported gemma-3-4b format-compliance signal was removed after re-scoring.
- The README now states that no variant separation has been observed in the local runs.
- The former “~7B capability edge” wording was downgraded to an experimental hypothesis.
- LM Studio generation metadata capture was strengthened.
- The benchmark self-test passed on the remediation commit.

This review does **not** validate ACL-ZH effectiveness. It validates the remediation of a benchmark measurement defect.

## 2. Current evidence boundary

Current local evidence is tracked as two separate families:

- **150 strict-diff inference runs**
- **60 edit-content diagnostic runs**

These counts must not be merged.

Current evidence does not support a claim that Baseline, Minimal ACL, or Full ACL is generally superior.

The observed local results currently show:

- smaller models can fall into format/serialization or semantic floors;
- stronger models can saturate the current task families;
- after scorer remediation, there is no surviving local variant-separation signal.

Therefore the next research step should improve discriminative power rather than search for a positive result by repeatedly adding similar runs.

## 3. Remaining P2 risks

### P2-A — Contract validation and literal fence text

Current edit-content contract validation rejects any content line whose left-trimmed text starts with:

```text
```
~~~
```

This is a conservative and defensible contract rule because Markdown fences are explicitly forbidden by the response contract.

However, there is a potential edge case: a valid source file may intentionally contain a line beginning with three backticks or three tildes as literal file content.

This is **not currently established as a bug**.

Before changing the scorer, determine whether the benchmark contract intends:

1. to forbid these literal line shapes unconditionally inside emitted file content; or
2. only to forbid Markdown wrapper syntax added by the model.

Do not relax the scorer post-hoc based on model output.

If this edge case is studied, first add a preregistered regression fixture and define the intended contract semantics before changing detection logic.

### P2-B — Historical rescoring depends on current scorer/oracle code

Raw responses are preserved, but rescoring still uses repository code supplied at score time.

A future change to:

- hidden oracles;
- task manifests;
- scorer logic;
- experiment configuration

could change the interpretation of historical raw responses.

Git commit capture helps, but file-level provenance should be stronger.

## 4. Required provenance hardening

Before the next major local-model experiment is promoted into README conclusions, result metadata should include hashes for the exact scoring inputs.

At minimum record:

- `git_sha`
- `manifest_sha256`
- `experiment_sha256`
- `scorer_sha256`
- `oracle_runner_sha256`

Recommended additional fields:

- `prompt_exporter_sha256`
- `parser_sha256` for edit-content track
- `run_manifest_sha256`

The purpose is not security. The purpose is to make historical rescoring auditable.

A result report should be able to answer:

> Which exact task definition, scorer, oracle implementation, parser, exporter, and experiment configuration produced this result?

## 5. Result immutability rule

Historical raw model responses are primary experimental records.

After a run is accepted:

- do not overwrite raw responses;
- do not replace them with regenerated model output;
- do not silently recompute and replace aggregate results without documenting the scorer/provenance change;
- when rescoring is required, retain the reason and the old-vs-new interpretation in the result report.

If a scorer defect is found, correction is allowed, but the repository must preserve an audit trail explaining:

1. what was wrong;
2. which historical runs were affected;
3. whether raw responses changed;
4. which derived metrics changed;
5. which README claims were retained, downgraded, or removed.

## 6. Next experimental phase

The next phase should focus on **benchmark discrimination**, not on increasing run counts alone.

The current 4B and 12B local observations suggest that an intermediate-capability model may be more informative on the current task family.

Testing a model around 7B is a reasonable next experiment-selection hypothesis.

It is not a validated capability threshold.

Allowed wording:

> The tested 4B and 12B conditions suggest that an intermediate capability range may provide more discrimination on the current tasks. A ~7B model is a reasonable next test condition.

Not allowed:

- “7B is the optimal model size.”
- “The threshold is proven to be 7B.”
- “Models below 7B are too weak.”
- “Models above 7B are too strong.”

These would overgeneralize from the current evidence.

## 7. Pre-run gate for the next model

Before executing the next local model condition, verify:

- [ ] task manifest is committed;
- [ ] experiment file is committed;
- [ ] prompt exporter is fixed;
- [ ] scorer is fixed;
- [ ] hidden oracle implementation is fixed;
- [ ] parser is fixed for edit-content track;
- [ ] No-op / Reference controls pass for the task manifest;
- [ ] response contract is frozen;
- [ ] decoding parameters are fixed;
- [ ] model identifier and quantization are recorded;
- [ ] context length is recorded;
- [ ] reasoning mode is recorded;
- [ ] provenance hashes are captured;
- [ ] no result-dependent parser/scorer modification is planned.

If any of these are not satisfied, the run should be considered exploratory rather than promotion-grade.

## 8. Post-run gate

Before adding a new local result to the top-level README:

- preserve raw responses;
- verify raw response count;
- verify run order;
- verify metadata;
- run strict or diagnostic scorer as preregistered;
- inspect failures without changing the scorer;
- confirm control results remain valid;
- record ceiling/floor conditions;
- compare variants only within the same model/runtime/contract;
- explicitly separate format compliance, semantic success, and contract-level task success;
- label null results as null results.

Do not promote a result merely because one variant has a numerically larger count in a very small sample.

## 9. Recommended next implementation task

Create a small provenance utility or integrate provenance capture into the existing local scoring path.

Suggested behavior:

```text
input:
  manifest
  experiment
  scorer
  oracle runner
  exporter
  parser (when applicable)

output:
  SHA-256 for each file
  git SHA
  track identifier
  result directory
```

The metadata should be written before or at scoring time and included in the result directory.

Do not make this utility mutate experiment inputs.

## 10. Acceptance criteria for the hardening follow-up

This follow-up is complete when:

- [ ] result provenance includes the exact scorer/oracle/task hashes;
- [ ] historical result reports can identify the scoring implementation used;
- [ ] the fence-literal edge case has a documented contract decision before any scorer change;
- [ ] next-model experiments pass the pre-run gate;
- [ ] no README statement presents the ~7B experiment choice as a validated threshold;
- [ ] strict-diff and edit-content tracks remain separated;
- [ ] benchmark self-test remains green.

## 11. Research interpretation

The benchmark is currently in a healthier state than before the remediation because a false-positive format-compliance signal was removed rather than defended.

That is desirable research behavior.

The next objective is not to recover a positive ACL-ZH effect.

The next objective is to create a test regime with enough measurement fidelity and task difficulty to detect either:

- a real variant effect;
- or a reproducible null result.

Both outcomes are valid.
