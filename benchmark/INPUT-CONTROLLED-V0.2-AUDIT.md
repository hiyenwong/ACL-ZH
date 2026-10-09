# Input controlled comparison v0.2 — information-equivalence audit

Status: **PRE-EXECUTION PASS WITH LIMITATIONS**

This audit was written before the first v0.2 model run.

## Arms

- `natural_vague`: pragmatic real-world baseline. It may omit explicit facts and is **not** used to isolate controlled-language form.
- `natural_matched`: ordinary Chinese prose containing the same required task facts as the controlled arms.
- `minimal_acl`: light controlled form with the same task facts.
- `full_acl`: structured controlled form with the same task facts.

The primary controlled-language contrasts are:

- `natural_matched` vs `minimal_acl`
- `natural_matched` vs `full_acl`
- `minimal_acl` vs `full_acl`

The contrast `natural_vague` vs the other arms measures a mixture of information explicitness and language structure and must be reported separately.

## Fact-set audit

For each of the six tasks, `natural_matched`, `minimal_acl`, and `full_acl` preserve the same intended facts:

| Task | Required behavioral fact | Scope / protected files | Compatibility / constraint | Acceptance check |
| --- | --- | --- | --- | --- |
| scope-01 | trim returned name | same allowed + forbidden files | preserve `get_user(user_id)` | same unittest command |
| reference-01 | parse debug string booleans + call `parse_config` | same allowed files | return dict; no other files | same unittest command |
| multi-action-01 | true/false string mapping + tests | same allowed files; schema protected | no other files | same unittest command |
| flow-01 | cache hit return; miss calls existing query once | same allowed files | preserve miss return behavior | same unittest command |
| validation-01 | trim and collapse all whitespace | same allowed files | no other files | same unittest command / exit-0 criterion |
| dependency-01 | sorted compact JSON | same allowed files; requirements protected | no new dependency | same unittest command |

## Output protocol

The v0.2 parser is frozen before execution in `benchmark/local-model/run_controlled_v02.py`.

It accepts only an explicit path header followed by a fenced code block:

`<<<path/to/file>>>`

followed by complete file content in a code fence.

The parser does not repair syntax, infer missing paths, rewrite code, or silently clean semantic errors.

## Limitations

This is an internal equivalence audit, not an independent blinded review. Wording length and visual structure necessarily differ because those are part of the treatment. The six tasks are small synthetic Python tasks; findings must not be generalized to autonomous coding agents without replication.
