# Benchmark Methodology v0.1

## Purpose

This benchmark tests whether ACL-ZH improves agent behavior compared with ordinary Chinese prompts. It is explicitly designed to falsify ACL-ZH, not to demonstrate it.

## Variants

Each task has two semantically intended variants:

- **Baseline**: natural Chinese instruction.
- **ACL-ZH**: instruction rewritten using current ACL-ZH rules.

The repository must not claim downstream improvement from static language metrics alone.

## Phase 1: Static language comparison

Static analysis measures:

- prompt length;
- ambiguous-expression count;
- explicit structure markers;
- explicit flow markers;
- normative markers;
- exact identifier references;
- validation-evidence markers.

These metrics only measure properties of the instruction text. They do **not** measure coding-agent success.

## Phase 2: Agent A/B test

Run both variants against the same model, model version, repository fixture, permissions, reasoning level, and starting commit.

For each task and variant, use multiple repetitions. Randomize execution order.

Record:

1. task success;
2. first-pass success;
3. constraint violations;
4. unrequested changes;
5. wrong-file modifications;
6. tests passed;
7. clarification requests;
8. tool calls;
9. input/output tokens when available;
10. elapsed time;
11. changed-file count;
12. diff size.

## Primary metrics

The primary metrics are:

- Constraint Violation Rate;
- Unrequested Change Rate;
- First-pass Success Rate;
- Task Success Rate.

Token use and tool calls are cost metrics, not quality metrics.

## Rule ablation

If ACL-ZH beats baseline, run ablations. Remove one rule family at a time:

- Action;
- Reference;
- Constraint;
- Flow;
- Validation.

A rule family should not be retained only because it sounds reasonable. It should show measurable benefit, or serve a clearly documented safety/correctness requirement.

## Interpretation

Possible outcomes include:

- ACL-ZH improves reliability but costs more tokens.
- ACL-ZH helps weak/medium models but not strong models.
- Only some rule groups matter.
- Excessive structure harms performance.
- Baseline Chinese performs equally well or better.

All are valid experimental outcomes.
