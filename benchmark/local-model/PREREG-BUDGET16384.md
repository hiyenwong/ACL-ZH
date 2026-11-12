# 8B output-budget follow-up, 2026-11-12

Frozen before inference. Question: does increasing the output budget to
16384 reduce the previously observed reasoning truncation and permit a
meaningful paired language-variant comparison? This is a new decoding
condition, not a continuation or replacement of archived scores.

Model: deepseek/deepseek-r1-0528-qwen3-8b, MLX 4bit, as reported by
the local native model API. Advertised maximum context 131072; configured
context is unknown and recorded as null. No downloads or paid endpoints.
Temperature 0, top_p 1, seed 20261011, requested reasoning_effort none;
the runtime may ignore this request. Per-request timeout 1800 seconds.

Execute dependency-mirror v0.4 (12 calls), then constraint v0.3 (36 calls),
using the committed registered JSON run orders, unchanged from the prior
experiment. One stateless call per task/variant, no retries or independent
replication claim. All variants share decoding. Run the exact manifests'
No-op and Reference controls and scorer/provenance self-tests before inference.

Primary endpoint: contract task_success. Secondary: semantic_task_success,
format_compliant. Record finish_reason, usage, and per-task paired outcomes.
Compare truncation descriptively against the archived 4096 condition;
runtime/date differences prevent attributing changes solely to budget.
Do not pool manifests, historical conditions, or strict-diff outcomes.
Variant separation requires the same direction on both manifests and
multiple task support; isolated differences are exploratory, with no
significance or ACL effectiveness claim. Report floor/ceiling explicitly.

Failure precedence: truncation (finish_reason length), constraint violation,
contract failure, semantic failure, success. Preserve every raw response.
Stop on request, control, or provenance errors; no automatic retries,
parser relaxation, prompt changes, or scoring overrides. If the first
manifest truncates in at least 6/12 calls, score and preserve it, then stop
before the second manifest: this budget remains unsuitable.

Outputs are isolated by tracked run ID in project artifacts. Source and
configuration are committed before launch. No historical outputs change.
