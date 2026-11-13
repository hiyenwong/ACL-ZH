# Shared response transport adjustment, 2026-11-13

Parent: completed budget-16384 experiment, run ad7d19bf-24d4-4ce8-88cf-ab5644a022e2.
Parent established feasible decoding (1/48 truncation), not ACL effectiveness.

Hypothesis: an explicit FILE-prefix example, fence-free source presentation,
and a no-tools clarification reduce output-contract errors. This bundled
intervention cannot identify the contribution of any one component.
Only the common prompt wrapper changes; all three task instructions, source
contents, manifests, oracle, parser and response-contract v0.1 stay unchanged.
Prompt transport v2 does not relax the accepted response language.

Model, decoding, task order and endpoints remain as in PREREG-BUDGET16384.md:
DeepSeek R1 Qwen3 8B, reported 4bit, temperature 0, top_p 1, seed 20261011,
max_tokens 16384, requested reasoning_effort none, timeout 1800 seconds.
Configured context unknown. Execute 12 dependency-mirror then 36 constraint
calls, one stateless call per task/variant. Run controls before each manifest.
Primary endpoint is contract task_success; secondary semantic success and
format compliance. Report residual text, wrong/missing markers, fences,
truncation and semantic failures separately. No pooling historical attempts.

Historical parent/child comparison is exploratory: no randomized concurrent
wrapper control and no causal attribution solely to transport. Language
separation still requires consistent direction on both manifests; small-sample
differences cannot establish ACL effectiveness or harm. Record all outcomes,
including regression. Never reparse historical outputs with a relaxed parser.

Same stop rules: request/control/provenance error stops the run, no automatic
retry; at least 6/12 dependency-mirror truncations stops before constraint.
Preserve raw responses and use run-ID-isolated artifacts under transport-v2.
No model downloads, paid API calls, ablation, or changes to hidden oracles.
