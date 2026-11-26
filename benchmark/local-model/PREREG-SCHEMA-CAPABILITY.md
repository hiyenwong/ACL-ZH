# Local schema capability probe — 2026-11-14

Paper-inspired feasibility stage, not a task benchmark or a full CRANE implementation.
Parent transport-v2 established that a better common wrapper reduces format
errors but does not ensure semantic correctness. The next question is whether
this local 8B service honors response_format json_schema at all.

Six disjoint toy requests, paired plain/schema for cooperative, plain-text
conflicting, and wrong-type conflicting instructions. Exact order and schema
are frozen in probe_structured_output.py. No benchmark task content is used.
Same 8B model, reported 4bit, temperature 0, top_p 1, seed 20261011,
max_tokens 16384, requested reasoning_effort none, timeout 1800 seconds.
No model downloads or paid APIs; no forced unloading of other models.

Endpoints: HTTP acceptance, exact output schema compliance, finish_reason,
token usage and latency. Preserve request/response/error JSON before analysis.
A 400 explicitly mentioning schema/response_format is a measured rejection;
other transport errors stop the probe. No retries, repairs or text extraction.
Schema validity requires exact keys, status enum and integer count (not bool).

Even six successes cannot prove token-level masking or general compliance.
Do not confuse reasoning-budget truncation with API rejection. A schema that
constrains a toy object does not ensure arbitrary source content or grammar
termination. Check backend implementation before claiming a strict guarantee.

If feasible, design a separate versioned output track and information-equivalent
task study; never alter the historical FILE parser or retrospectively normalize
its outputs. That second-stage design depends on this probe's actual findings.
