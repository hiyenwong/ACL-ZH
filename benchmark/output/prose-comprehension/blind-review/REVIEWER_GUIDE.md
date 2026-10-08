# Reviewer Guide

You are reviewing whether three anonymous Chinese explanations contain the same information as a source fact sheet.

You are **not** evaluating which text is better written, easier to read, more professional, or more pleasant.

## What you receive

A self-contained HTML file.

For each item you will see:

- a Fact Sheet;
- Version A;
- Version B;
- Version C.

The identities of A/B/C are hidden.

## What to score

For each version, compare it only with the Fact Sheet.

### Fact Coverage

- `pass`: all material facts are preserved.
- `minor`: a small detail is weakened or less explicit.
- `fail`: a material fact is missing.

### Extra Information

- `none`: no additional substantive fact.
- `minor`: small explanatory wording that does not change the information set.
- `material`: new substantive information appears.

### Semantic Drift

- `none`: meaning is preserved.
- `minor`: wording shifts nuance but not the core claim.
- `material`: meaning changes materially.

### Terminology Drift

- `none`: terminology is materially equivalent.
- `minor`: terminology changes slightly without changing the concept.
- `material`: terminology change can alter interpretation.

### Answer Leakage

This asks whether presentation gives an unusual cue that makes a later question easier independently of the underlying facts.

- `none`
- `low`
- `material`

### Overall Equivalent

Choose `true` only if the version can fairly be treated as the same information as the Fact Sheet.

## What not to do

Do not:

- guess which version is ACL-ZH;
- search the public repository for the mapping;
- compare your results with another reviewer;
- score style preference;
- score visual attractiveness;
- change an earlier score because another version seems better.

## Finish

Enter a pseudonymous Reviewer ID.

When all items are complete, click **导出 review JSONL** and return the exported file to the coordinator.

Do not include your real name in the JSONL file.
