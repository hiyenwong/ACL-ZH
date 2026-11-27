# Free-answer schema semantic probe — result report

Run: 40e6d411-29c4-4091-8dfd-52f26ffc4a66. Source commit: 346f051.
Date: 2026-11-18. Model: deepseek/deepseek-r1-0528-qwen3-8b, reported 4bit.
Temperature 0, top_p 1, seed 20261011, max_tokens 16384, requested
reasoning_effort none. Ten fresh tasks (five arithmetic, five miniature code
transformations) were each run once plain and once with a JSON Schema that did
not contain the answer. All 20 requests returned HTTP 200 with finish_reason
stop; no call truncated. The pre-run task/evaluator self-test passed.

## Observed outcomes

| Condition | n | Exact schema valid | Semantic valid | Both | Truncated | Reported reasoning_tokens=0 |
|---|---:|---:|---:|---:|---:|---:|
| Plain exact-JSON instruction | 10 | 0 | 5 | 0 | 0 | 0 |
| response_format json_schema | 10 | 10 | 0 | 0 | 0 | 10 |

By task family, plain semantic validity was arithmetic 4/5 and code 1/5;
constrained semantic validity was 0/5 in both families. Constrained arithmetic
answers were all wrong: 4, -492, 47, 42, and 42 where the five expected values
were 9, 184, 201, 46, and 40. This arithmetic result is deterministic and does
not depend on the narrow code-expression evaluator.

The constrained mode emitted the exact required object shape in every call, but
did so without reported reasoning tokens and with very short completions. The
plain mode spent 225–9,870 reported reasoning tokens per call and often reached
the right arithmetic value despite violating the exact object contract.

## Design defect and evidence boundary

The plain prompt asked for `task_id` but did not state the expected task ID;
the constrained schema supplied that ID through an enum. Therefore the 0/10
plain exact-schema rate is not a fair instruction-following comparison. A
post-hoc inspection shows 9/10 plain responses were JSON-parseable; most failed
the exact contract because they invented a different task ID, and one wrapped
the object in a Markdown fence. This post-hoc count is diagnostic only and was
not a preregistered endpoint.

The code semantic endpoint is also intentionally narrow. The evaluator accepts
only a whitelist of expression nodes and never executes generated Python. At
least one constrained response was semantically plausible but used syntax
outside the whitelist (`in` inside a conditional expression), so code semantic
validity can undercount equivalent expressions. Arithmetic correctness is not
affected by this limitation.

Post-hoc audit note (added 2026-11-27; archived requests/responses immutable):
in this historical run (`346f051`), the three code tasks `code-normalize-01`,
`code-distance-01`, and `code-list-01` did not explicitly identify the input
variable names bound by `semantic_valid()` (`value`, `left`/`right`, and
`items`). As a result, reasonable expressions using alternative variable names
failed evaluation — notably constrained `03-response.json`
(`s.strip().lower()`, which matches the requested normalization but failed
because only `value` is bound) and `11-response.json`
(`[x.strip().strip() for x in list]`), as well as plain `08-response.json`
(`abs(5 - 3)`) and `12-response.json` (`[s.strip() for s in input_list if
isinstance(s, str)]`). Accordingly, the archived code semantic validity rates
(`0/5` constrained, `1/5` plain) conflate input-binding underspecification with
genuine semantic failures and must not be interpreted on their own as pure
code-reasoning failure. The current script
(`benchmark/local-model/probe_free_answer_schema.py`) now specifies these
input bindings and implements Python short-circuit operand-returning `BoolOp`
(`and`/`or`) semantics for any future re-runs (verified that `0/10` archived
code responses in this run used `and`/`or`, so historical scores are
unaffected), while all archived JSON files in this directory remain unchanged. The non-promoting decision for this schema route
rests on the deterministic arithmetic probe (constrained `0/5` vs plain `4/5`,
with `0` reported reasoning tokens on every constrained call), which does not
depend on code variable bindings or the AST evaluator.

The primary conclusion is the constrained semantic regression on arithmetic:
5/5 plain arithmetic answers were not matched by the constrained mode, which
was 0/5 and used no reported reasoning tokens. This is a small, one-call-per-
condition diagnostic, not a significance test or evidence about ACL variants.

## Interpretation

The local `response_format json_schema` path does not merely constrain the
final surface form in this runtime. In these runs it changed the effective
generation path: all constrained calls reported zero reasoning tokens and all
produced syntactically valid guesses rather than computed answers. This is the
opposite of the desired CRANE-style separation, where reasoning remains free
and only the final answer is constrained.

Do not adopt this schema path for the formal ACL-ZH code track. The earlier
transport-v2 prompt remains the safer existing option because it preserved
reasoning and improved format compliance without disabling the reported
reasoning channel. A future structured-output implementation must explicitly
separate unconstrained reasoning from constrained final emission and demonstrate
both semantic preservation and grammar compliance on free-answer tasks.

## Next decision

1. Treat this schema route as non-promoting for ACL-ZH benchmark use.
2. Keep transport-v2 as the current candidate prompt transport.
3. Before another model run, complete the atomic-requirement and information-
   equivalence audit across Baseline / Minimal / Full instructions.
4. If structured output is revisited, use a backend/runtime where free reasoning
   and a constrained final channel are demonstrably independent; repeat this
   free-answer gate before any benchmark-scored calls.

Raw requests, responses, configuration, and summary remain immutable in this
directory. No historical output was rescored or pooled with this probe.
