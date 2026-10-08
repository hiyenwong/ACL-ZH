# Input Track Rule-family Ablation v0.1

Ablation is only interpretable if task information is held constant.

Therefore ACL-ZH does **not** define `Full - Constraint` as deleting the underlying constraint facts. It removes the controlled-language mechanism used to express that family while preserving the task facts in less controlled prose.

Variants:

- `full`
- `full_minus_action`
- `full_minus_reference`
- `full_minus_constraint`
- `full_minus_flow`
- `full_minus_validation`

## Interpretation

The comparison asks whether the expression rules in one family contribute incremental value beyond the same underlying information.

It does not ask whether agents perform better when information is removed.

## Gate

Do not spend model runs on ablation until the primary Baseline / Minimal / Full experiment shows a meaningful signal, unless ablation is being used only as a harness smoke test.
