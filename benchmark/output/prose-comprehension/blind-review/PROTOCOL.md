# Independent Blind Review Protocol v0.1

## Purpose

This protocol verifies information equivalence without revealing which text is Natural Chinese, Light ACL, or Full ACL.

The reviewer evaluates content, not style preference.

## Materials

Generate a blinded package:

```bash
python benchmark/output/prose-comprehension/blind-review/anonymize.py \
  --items benchmark/output/prose-comprehension/items/items-v0.2.jsonl \
  --seed 20261008 \
  --out-dir /tmp/aclzh-blind
```

The command produces:

- `review-pack.jsonl`: safe to give to reviewers;
- `answer-key.jsonl`: keep hidden until reviews are complete.

## Reviewer task

For every A/B/C version, compare the text only against the fact sheet.

Score:

- Fact Coverage
- Extra Information
- Semantic Drift
- Terminology Drift
- Answer Leakage
- Overall Equivalent

Do not score readability, elegance, preference, or which version you think is ACL-ZH.

## Blinding rules

Reviewers must not receive:

- variant names;
- the answer key;
- project hypotheses about which version should perform better;
- prior audit results.

The review coordinator should avoid revealing characteristic ACL-ZH labels or naming conventions outside the text itself.

## Minimum review gate

For a pilot human study:

- at least 2 independent reviewers;
- no material issue from either reviewer;
- both reviewers mark every version overall-equivalent.

For publication-quality work, use at least 3 reviewers and report disagreement.

## Disagreement

If reviewers disagree:

1. retain all original review rows;
2. do not silently overwrite scores;
3. perform adjudication with a new reviewer or documented discussion;
4. publish pre- and post-adjudication results separately.

## Limitation

Blinding hides the source variant identity, but reviewers may infer style from the text. This is unavoidable and must be reported.
