# Controlled v0.2 run 37911508924 — INVALIDATED

Status: **INVALID — scorer implementation defect**

The model runs completed, but the preregistered parser contained an escaping bug.

The intended regex was to match:

`<<<path/to/file>>>`

followed by a fenced code block.

The committed implementation accidentally double-escaped whitespace/newline tokens (for example `\\s` and `\\n` inside a Python raw regex), causing valid model responses to be recorded as `parsed_file_count = 0`.

Raw artifacts show that the model did emit the expected path-header + fenced-code structure.

Therefore:

- the 24 inference outputs are real;
- the published aggregate from this workflow is **not a valid performance result**;
- no ACL-ZH conclusion may be drawn from run `37911508924`;
- the parser must be fixed and self-tested before rerunning the experiment.

This invalidation was recorded before the corrected rerun.
