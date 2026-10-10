# Local Open-Model Smoke Diagnostic

Date: 2026-10-10

## Scope

Two deterministic local open-model smoke experiments were executed with the same six tasks, three prompt variants, randomized order, and hidden-oracle scorer:

- Qwen/Qwen2.5-Coder-0.5B-Instruct
- Qwen/Qwen2.5-Coder-1.5B-Instruct

Each experiment used 18 first-shot generations: 6 tasks × Baseline / Minimal ACL / Full ACL.

## Result

For both model sizes, strict scoring produced 0/18 patch applications and 0/18 task successes.

A diagnostic pass removed only an outer Markdown `diff` fence. It did not repair code or patch structure. Fence-normalized scoring also produced 0/18 patch applications for both model sizes.

## Important interpretation

This is a floor effect at the patch-serialization layer. It is not evidence that ACL-ZH has no effect.

Inspection of the 1.5B raw outputs shows that some generations contain semantically plausible or correct edits but invalid unified-diff structure.

Examples:

- `validation-01:minimal` changes `value.strip()` to `' '.join(value.split())`, which is directionally correct for internal whitespace normalization, but the generated hunk header claims line counts that do not match the source fixture.
- `scope-01:full` changes the returned name from `'  Alice  '` to `'Alice'`, which is the intended edit, but again uses a fabricated hunk shape.
- Other outputs contain genuine semantic failures, such as modifying `schema.json` for `multi-action-01` or altering tests unnecessarily.

Therefore the current 0/18 outcome conflates at least two failure classes:

1. patch serialization / unified-diff validity failure;
2. actual task-solving or constraint-following failure.

## Evidence boundary

Do not use these runs to claim that Baseline, Minimal ACL, or Full ACL is better or worse.

The experiment currently measures the model's ability to emit a directly `git apply`-compatible patch under the response contract. For 0.5B and 1.5B, that contract creates a floor effect.

## Next experiment

Use a stronger fixed model while preserving the same tasks, prompt variants, order, deterministic decoding, and scorer.

Recommended next step: Qwen2.5-Coder-3B-Instruct.

If 3B still shows a patch-serialization floor, add a separately labeled `edit-content` diagnostic track that evaluates requested file content independently of unified-diff serialization. Do not merge that track with strict patch results.
