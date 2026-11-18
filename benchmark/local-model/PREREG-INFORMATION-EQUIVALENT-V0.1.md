# Preregistration: Information-equivalent edit-content manifest v0.1

Prereg ID: `prereg-information-equivalent-v0.1`
Date frozen: 2026-11-18
Parent: completed transport-v2 run `a52f5cf4-8c79-4cf3-825c-1e0b145ec0da`
(experiment `364c028e-24af-4a1c-b749-60a3ba35afa0`).

## Research question

When Baseline, Minimal ACL, and Full ACL prompts disclose exactly the same
atomic facts, modification scope, and evaluator-only validation information,
does prompt presentation alone change edit-content task success for the fixed
local 8B model?

This is the first confirmatory-track attempt after the v0.1 audit found that
the historical 16-task set had unequal information and constraint hardness.
Both a null result and a presentation separation are valid outcomes.

## Construction boundary

- Tasks: 12 fresh held-out Python edit tasks with new task IDs and new source
  files. None was used for transport-wrapper tuning.
- Manifest: `benchmark/tasks/manifest-information-equivalent-v0.1.jsonl`.
- Fact ledger: 56 counted technical atomic facts plus one counted scope fact
  and one uncounted evaluation disclosure per task.
- Every variant renders every atomic fact verbatim with the same stable fact ID.
  Fact hardness is `required` in every variant.
- The only permitted variant-only lines are generic section framing lines.
  `benchmark/local-model/audit_information_equivalence.py` rejects any other
  variant-only content.
- All prompts say that the evaluator will run tests after receiving complete
  files. No prompt tells the no-tool model to run tests.

## Fixed conditions

- Model: `deepseek/deepseek-r1-0528-qwen3-8b`, reported quantization `4bit`.
- Response transport: explicit transport v2 and edit-content contract v0.1.
- Decoding: temperature 0, top_p 1, seed 20261011, max_tokens 16384,
  requested reasoning effort `none`, request timeout 1800 seconds.
- Variants: baseline, minimal, full; one stateless call per task×variant,
  36 scored calls total.
- Run order: sorted `task:variant` strings shuffled by
  `random.Random(20261011)`; the exact order is pinned in
  `benchmark/local-model/registered-information-equivalent-v0.1.json`.
- Repetitions: 1. Identical deterministic outputs are not treated as
  independent replications.

## Mandatory pre-inference gates

The run must stop before model inference unless all gates pass:

1. strict information-equivalence audit reports 12 tasks, 56 technical facts,
   and zero errors;
2. No-op controls score 0/36 across all three variants;
3. Reference controls score 36/36 across all three variants;
4. the registered experiment validates its task/run-order closure;
5. manifest task IDs exactly match the registered task IDs;
6. provenance is captured without a version mismatch.

## Outcomes

Primary endpoint per variant: `task_success` (semantic task success and format
compliance). Secondary endpoints: `semantic_task_success` and
`format_compliant`. Diagnostics: truncation, parsed block count, format
violations, hidden-oracle failures, visible-test failures, and scope violations.

Analysis is paired by task. Report the full task×variant matrix and raw counts
for each endpoint. With 12 tasks, no p-value or confidence-interval claim is
made. A follow-up-only signal requires a variant to have at least four net
paired task-success wins over each other variant without ceiling or floor
saturation. A single such run does not establish ACL effectiveness; it only
justifies a fresh preregistered replication.

If 12 or more of 36 generations report `finish_reason=length`, variant
comparison is labeled truncation-confounded. Any request, control, provenance,
or scoring error stops the run without automatic model retry.

## Interpretation limits

This experiment tests residual presentation differences after machine-checked
information equivalence. It does not prove that paraphrases are cognitively
equivalent to a human, does not validate JSON Schema constrained decoding, and
does not pool results with the historical dependency-mirror, constraint, or
strict unified-diff tracks. Historical transport-v2 comparisons remain
exploratory because their task information was unequal.

## Repair amendment A1, 2026-11-18

The first submitted run `1f40c7a5-a5fe-4d1f-a532-18cdf2a739e0` completed every
construction gate, then LM Studio returned `{"error":"Model unloaded."}` on
request 6 after five partial generation attempts. It established no scored
variant result and its partial responses are not scored or pooled.

Before the repair attempt, the target model is explicitly loaded as
`deepseek/deepseek-r1-0528-qwen3-8b@4bit` with configured context length
32768, parallelism 1, and a 24-hour keep-alive TTL. The repair records
context length 32768 in generation metadata. Tasks, prompts, model, decoding,
max completion tokens, scorer, oracle, and analysis plan are unchanged.
