# Blind Review Coordinator Runbook

## Goal

Create a reviewer package without exposing Natural / Light ACL / Full ACL identities.

## Generate a private mapping

For a real review, do not pass `--seed`.

```bash
mkdir -p private/blind-v0.2
python benchmark/output/prose-comprehension/blind-review/anonymize.py \
  --items benchmark/output/prose-comprehension/items/items-v0.2.jsonl \
  --out-dir private/blind-v0.2
```

The command creates `review-pack.jsonl` and `answer-key.json`. Keep the answer key private and do not commit the generated files while review is active.

## Build reviewer HTML

```bash
python benchmark/output/prose-comprehension/blind-review/build_reviewer_html.py \
  --review-pack private/blind-v0.2/review-pack.jsonl \
  --output private/blind-v0.2/reviewer.html
```

Send only `reviewer.html` to reviewers. It is self-contained and runs locally in a browser.

## Collect and validate

Each reviewer exports one JSONL file.

```bash
python benchmark/output/prose-comprehension/blind-review/validate_reviews.py \
  reviewer-01.jsonl reviewer-02.jsonl
```

Each reviewer must produce exactly 30 review cells.

## Aggregate while still blind

```bash
python benchmark/output/prose-comprehension/blind-review/aggregate_reviews.py \
  reviewer-01.jsonl reviewer-02.jsonl
```

Record the gate decision before opening `answer-key.json`.

## Unblind

Only after the blind gate decision is frozen should the coordinator open the key.

Publish pseudonymous reviewer rows, aggregate results, the mapping key, reviewer count, and any adjudication record. Never publish real reviewer identities.
