# 2026-11 research progress

Updated: 2026-11-26.

This report covers the registered local-model experiments that followed the
October LM Studio studies. These are diagnostic edit-content, structured-output
and mechanism results, not autonomous Claude Code / Codex benchmark results.

## Current status

- **ACL effectiveness remains unvalidated.** No completed run supports a general
  claim that Baseline, Minimal ACL and Full ACL differ in task success.
- **Transport-v2 is the retained response-contract candidate.** It reduced
  formatting failures in one historical condition, but did not establish an ACL
  language effect.
- **The tested `response_format=json_schema` route is non-promoting.** It achieved
  exact schema compliance while destroying semantic accuracy on the free-answer
  probe.
- **The latest information-equivalent comparison is complete.** All completed
  responses succeeded; every observed failure was hidden-reasoning budget
  exhaustion.
- **nanochat is a separate mechanism study.** It measures the cost of suppressing
  visible reasoning and is not an ACL effectiveness experiment.

## Registered experiment sequence

| Study | Run / source | Observed result | Committed evidence & preregistration | Decision |
| --- | --- | --- | --- | --- |
| 8B, 16,384-token budget | `ad7d19bf-24d4-4ce8-88cf-ab5644a022e2` / `3267889` | 48/48 calls. Dependency-mirror contract success 0/4 for every variant; constraint Baseline/Minimal/Full 8/12, 6/12, 4/12. | [Report](local/2026-11-13-deepseek-r1-8b-budget16384-edit-content/RESULT-REPORT.md) · [Prereg](../local-model/PREREG-BUDGET16384.md) | No preregistered cross-manifest separation; inspect failure taxonomy and information equivalence. |
| Explicit response transport v2 | `a52f5cf4-8c79-4cf3-825c-1e0b145ec0da` / `b584045` | 48/48 calls. Dependency-mirror 1/4 per variant; constraint Baseline/Minimal/Full 10/12, 11/12, 9/12. Format compliance improved, semantics did not improve uniformly. | [Report](local/2026-11-13-deepseek-r1-8b-transport-v2-edit-content/RESULT-REPORT.md) · [Prereg](../local-model/PREREG-TRANSPORT-V2.md) | Retain as a candidate transport; no ACL efficacy or harm claim. |
| JSON Schema capability probe | `91d11517-f949-4bff-ac82-ccf1105600d5` / `83d2f59` | 6/6 calls. Constrained responses were schema-valid 3/3 versus plain 1/3, but singleton enums supplied the entire answer. | [Report](local/2026-11-14-deepseek-r1-8b-schema-capability-probe/RESULT-REPORT.md) · [Prereg](../local-model/PREREG-SCHEMA-CAPABILITY.md) | Structural feasibility only; require free-answer semantic tests. |
| Free-answer schema semantic probe | `40e6d411-29c4-4091-8dfd-52f26ffc4a66` / `346f051` | 20/20 calls. Constrained exact-schema 10/10, arithmetic 0/5, code 0/5 (overall 0/10); plain arithmetic 4/5, code 1/5 (overall 5/10). Note: 3 historical code prompts omitted input variable names (see report). | [Report](local/2026-11-18-deepseek-r1-8b-schema-free-answer-probe/RESULT-REPORT.md) · [Prereg](../local-model/PREREG-FREE-ANSWER-SCHEMA.md) | Reject this schema path based on deterministic arithmetic regression (0/5 vs 4/5); retain transport-v2. |
| Information-equivalent edit-content v0.1 | `c7ab1518-ab20-472c-8c6e-fcf67bf71206` / `082d13c` | 36/36 calls. Baseline/Minimal/Full task success 11/12, 10/12, 10/12; all 31 non-truncated calls passed. | [Report](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/RESULT-REPORT.md) · [Prereg](../local-model/PREREG-INFORMATION-EQUIVALENT-V0.1.md) · [Manifest](../tasks/manifest-information-equivalent-v0.1.jsonl) | No follow-up gate met; do not claim an ACL effect or tune on the same tasks. |
| d12 reasoning-suppression mechanism | `548d036b-3882-49d4-8f57-62f082ac0115` / `58ef5bd` | d12 trace arm: silent multi-digit 0.3737, visible 1.000; direct arm: silent multi-digit 0.3434, trace-requested 0.3131 with no visible work. | [Report](local/2026-11-25-nanochat-d12-suppression-mechanism/RESULT-REPORT.md) · [JSON](local/2026-11-25-nanochat-d12-suppression-mechanism/d12-suppression-report.json) · [Prereg](../local-model/PREREG-NANOCHAT-SUPPRESSION-V0.1.md) | Depth narrows but does not close the suppression gap; training budget remains confounded. |

All listed model runs are terminal, and all six source commits are ancestors in
this repository's git history. Earlier interrupted or implementation-failed
runs are not pooled into these measurements. In the archived 2026-11-18
free-answer schema probe (`40e6d411-29c4-4091-8dfd-52f26ffc4a66`), three code
prompts (`code-normalize-01`, `code-distance-01`, `code-list-01`) omitted the
evaluator's bound variable names (`value`, `left`/`right`, `items`), so the
archived code-semantic rate conflates underspecified bindings (e.g.,
`03-response.json` returning `s.strip().lower()`) with genuine semantic
failures; `probe_free_answer_schema.py` has since been fixed for future runs
without altering archived outputs, and the rejection of this schema route
rests on the deterministic arithmetic probe (constrained 0/5 vs plain 4/5,
with zero reported reasoning tokens under constrained decoding).

## Latest primary Input Track result

The [information-equivalent manifest](../tasks/manifest-information-equivalent-v0.1.jsonl)
passed all construction gates defined in
[PREREG-INFORMATION-EQUIVALENT-V0.1.md](../local-model/PREREG-INFORMATION-EQUIVALENT-V0.1.md)
before inference: 12/12 tasks and 56 counted technical facts passed the
[equivalence audit](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/pre-inference-equivalence-audit.json);
[No-op controls](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/controls-noop.json)
were 0/36 and
[Reference controls](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/controls-reference.json)
36/36. Scoring provenance in
[aggregate-edit-content.json](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/equivalence/aggregate-edit-content.json)
was verified without overrides.

| Variant | Task success | Semantic success | Format compliance | Truncated |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 11/12 | 11/12 | 11/12 | 1/12 |
| Minimal ACL | 10/12 | 10/12 | 10/12 | 2/12 |
| Full ACL | 10/12 | 10/12 | 10/12 | 2/12 |

Every failure used the full completion budget, reported 16,382 hidden reasoning
tokens, returned zero visible content and contained no file blocks. Thus the
11/10/10 split is a distribution of budget exhaustion, not evidence for or
against ACL structure. The preregistered follow-up threshold of at least four
net paired wins was not met: Baseline was only +1 over Minimal and +1 over Full;
Minimal and Full had identical task outcomes.

## Reasoning-suppression mechanism result

nanochat provides one visible assistant channel, so every generated token is
supervised and countable. Under direct instructions, both d12 arms emitted zero
visible work. The trace-trained arm reached 1.000 accuracy with visible work but
0.690 overall and 0.3737 multi-digit accuracy when silent. The direct-trained
arm reached 0.675 overall and 0.3434 multi-digit accuracy when silent.

Compared with the d6 one-epoch arms, d12 silent multi-digit accuracy improved
from 0.2222 to 0.3737 for the trace arm and from 0.1515 to 0.3434 for the direct
arm. However, the d6 direct-2x arm reached 0.6667 silent multi-digit and 0.835
overall silent accuracy, exceeding the d12 one-epoch direct arm. Capability and
training budget therefore cannot be separated by the d12 result alone.

These are deterministic synthetic-addition mechanism runs with unequal
trace/direct SFT budgets. They support no ACL claim and no general language-model
scaling law.

## Evidence boundary and next gate

1. One deterministic call per condition is not an independent replicated effect.
2. Edit-content success is not strict unified-diff success or autonomous-agent
   success; tracks must remain separate.
3. Hidden-reasoning truncation must be classified as budget exhaustion, not as a
   semantic or ACL formatting failure.
4. The next ACL effectiveness study needs a fresh, harder held-out task set or a
   preregistered reasoning/budget control. Retuning on the 12 information-
   equivalent tasks and then reusing them as confirmation is not valid.
5. A d12 direct-2x condition would isolate more of the training-budget question,
   but it is a new mechanism experiment, not a prerequisite for adopting ACL-ZH.
