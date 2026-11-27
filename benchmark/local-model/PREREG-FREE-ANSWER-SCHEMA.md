# Free-answer schema semantic probe — 2026-11-18

Parent run 91d11517 established that the local API accepts a fixed-answer
schema and changes observed output behavior. It did not test semantics because
the schema contained the entire answer. This child uses ten fresh, non-benchmark
tasks and twenty paired calls to test whether structural constraint remains
useful when values must be computed.

Five arithmetic and five miniature Python-transformation tasks are used. For
each task, one plain call receives the same exact-JSON instruction as one
constrained call; only the latter supplies response_format json_schema. The
schema restricts object keys and types, but contains no expected answer or
expected expression. Fixed interleaved order is frozen in
probe_free_answer_schema.py.

Model: deepseek/deepseek-r1-0528-qwen3-8b, reported 4bit. Temperature 0,
top_p 1, seed 20261011, max_tokens 16384, requested reasoning_effort none,
per-request timeout 1800 seconds. One stateless call per condition, no retries,
no benchmark prompt reuse, and no independent-replication claim.

Endpoints:
- schema validity: exact keys, exact task id, integer answer or nonempty string expression;
- semantic validity: arithmetic equals the expected value; code passes all
  predetermined input/output cases through a whitelist AST evaluator;
- truncation, reported reasoning tokens, and latency;
- combined format-and-semantics success.

The code evaluator intentionally supports only the expression nodes needed by
the task set. It never executes generated Python as a program and rejects
imports, lambdas, statements, unknown names, unknown methods, and unsupported
operations. A semantically equivalent expression using unsupported syntax is
classified false under this narrow endpoint; this limitation is reported.

Primary interpretation is paired task-level behavior. With one deterministic
call per condition, no significance or general superiority claim is allowed.
If constrained calls report zero reasoning tokens again, treat that as an
observed usage/configuration difference and do not infer that reasoning is
impossible. A regression in semantic correctness is as informative as an
improvement. No historical outputs are rescored.

Stop on any HTTP/transport error. A 400 response is an infrastructure or API
compatibility result, not a model failure. Preserve every request and response.
No paid API, model download, ACL efficacy claim, or edit-content score pooling.
