# Local JSON Schema capability probe — completed

Run 91d11517-f949-4bff-ac82-ccf1105600d5; source commit 83d2f59.
Six request/response pairs preserved, all HTTP 200, no truncation.

| Prompt | Plain schema-valid | Constrained schema-valid |
|---|---|---|
| Cooperative | yes | yes |
| Requests plain text | no | yes |
| Requests wrong types/extra key | no | yes |

All constrained responses are exactly the same valid object:
{"status": "ACLZH_PROBE_OK", "count": 7}.
Thus this request shape is accepted and the observed response behavior changes
under response_format. It is not sufficient to prove a general token-mask guarantee.

## Critical limitations

Both output fields are singleton enums: the schema itself encodes the entire
answer. This deliberately adversarial feasibility test measures structural
control, NOT reasoning, instruction comprehension, code correctness or ACL
benefit. A backend can satisfy it without solving a task.

Reported reasoning_tokens are 0 for all constrained cases versus 58, 1656,
and 648 in the plain cases. This is an observation about reported usage,
not proof that all internal reasoning is disabled or that a particular
implementation is active. Runtime inspection and nonconstant-content tests
are needed before extrapolation to coding tasks. Do not treat the dramatic
latency difference on trivial fixed-answer cases as a general speedup.

This is not a CRANE implementation: no explicit switching between free
reasoning and constrained final generation has been implemented or verified.

## Next protocol gate

Before a formal code study, use schemas with free answer/content fields whose
correct values are NOT supplied by the schema. Pair constrained/plain output
on identical unseen arithmetic and miniature code tasks, test semantics with
deterministic checks, and record reasoning usage separately. Then design a
new versioned code-output track with information-equivalent prompt variants.
Never rescore historical FILE outputs using a JSON parser.

No further compute launched in this analysis turn.
