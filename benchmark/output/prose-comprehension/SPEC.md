# Output Track: Prose Comprehension v0.1

## Goal

This track tests whether controlled Chinese improves how humans understand model-generated technical explanations.

It does not test whether ACL-ZH helps an agent execute code changes.

## Research question

Given the same underlying technical facts, does controlled Chinese improve:

- comprehension accuracy;
- answer lookup speed;
- retention;
- error rate;
- perceived cognitive load?

## Experimental arms

### O0 — Natural Chinese
Normal high-quality technical Chinese.

### O1 — Light ACL
Apply only high-value clarity rules:
- explicit subjects and objects;
- fewer ambiguous references;
- explicit conditions;
- consistent terminology.

### O2 — Full ACL
Apply the full current ACL-ZH prose rules.

### O3 — Diagram-first
Present the same information primarily as a diagram with short labels.

### O4 — Interactive HTML
Present the same information as a small interactive explainer.

O3 and O4 are separate modality experiments. They must not be used to claim that controlled language alone caused an effect.

## Information-equivalence requirement

All arms must encode the same source facts.

A hidden fact sheet is the source of truth. Human-facing variants may reorder or reformat facts, but may not add or remove substantive information.

## Participant tasks

For each explanation, participants answer:

1. factual recall questions;
2. inference questions;
3. locate-a-detail questions;
4. confidence rating;
5. perceived cognitive-load rating.

## Primary metrics

- Comprehension Accuracy
- Median Time to Correct Answer
- Misinterpretation Rate
- Delayed Recall Accuracy

## Secondary metrics

- self-reported cognitive load;
- confidence calibration;
- reading time;
- preference.

Preference is not a substitute for comprehension.

## Suggested derived metric

An exploratory metric may be reported as:

`Understanding Efficiency = Correct Answers / Time`

This is not a validated psychometric construct and must be labeled exploratory.

## Bias controls

- randomize presentation order;
- counterbalance variants;
- do not show the same participant multiple versions of the same item unless using a crossover design with washout;
- blind scorers to output variant where manual scoring is required;
- separate technical expertise strata;
- report native-language proficiency.

## Initial domains

Start with short technical explanations where correctness can be scored objectively:

- HTTP reverse proxy behavior;
- database transaction isolation;
- caching and fallback flow;
- authentication token lifecycle;
- data pipeline failure recovery.

Avoid opinion-heavy topics in the first phase.

## Publication rule

Do not claim “ACL-ZH is easier to understand” until human-subject data exists.

Model-generated readability scores alone are insufficient evidence.
