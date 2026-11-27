# Input Track execution status

## Current status — 2026-11-26

The local 8B diagnostic line has completed its information-equivalent v0.1
comparison. Baseline / Minimal ACL / Full ACL task success was 11/12, 10/12 and
10/12. Every completed response passed semantics and format; all five failures
were hidden-reasoning budget truncations. The preregistered follow-up gate was
not met, so no ACL effect or harm claim is supported.

Transport-v2 remains the candidate response contract. The tested JSON Schema
route was rejected after exact schema compliance coincided with 0/5 arithmetic
accuracy (vs 4/5 plain; 0/10 overall semantic, noting that 3 historical code
prompts omitted explicit input variable names) on the free-answer probe. The
d12 nanochat suppression study is complete but belongs to the separate mechanism
track, not the ACL effectiveness result (post-hoc audit also confirmed the
historical d6/d12 eval split overlapped training on 199/200 operand pairs and
389/400 exact prompts; future splits are now enforced disjoint).

The next valid effectiveness study requires a fresh harder held-out task set or
a preregistered reasoning/budget control. The 12 information-equivalent tasks
must not be retuned and then reused as independent confirmation.

Full run IDs, commits, committed archives and evidence boundaries:
[2026-11 research progress](2026-11-RESEARCH-PROGRESS.md)
(primary archive: [2026-11-18-deepseek-r1-8b-information-equivalent-v0.1](local/2026-11-18-deepseek-r1-8b-information-equivalent-v0.1/RESULT-REPORT.md),
manifest: [manifest-information-equivalent-v0.1.jsonl](../tasks/manifest-information-equivalent-v0.1.jsonl),
preregistration: [PREREG-INFORMATION-EQUIVALENT-V0.1.md](../local-model/PREREG-INFORMATION-EQUIVALENT-V0.1.md)).

The autonomous Claude Code / Codex smoke workflows below remain credential
blocked; their historical status is unchanged.

## Smoke run attempt

Workflow run: 37790448253

Commit: `98d118b5909fa1f75f5b36e45e21c615983e5b96`

Planned smoke matrix:

- Codex: 6 tasks × 3 variants × 1 repetition
- Claude Code: 6 tasks × 3 variants × 1 repetition

Observed result:

| Agent | Credential check | Agent installed | A/B run | Result |
| --- | --- | --- | --- | --- |
| Codex | no credential available | skipped | skipped | blocked |
| Claude Code | no credential available | skipped | skipped | blocked |

The workflow itself completed the credential-gating path correctly and uploaded status artifacts.

No model-performance result exists from this run.

## Required repository credentials

At least one of these must be configured before a real run can execute:

- `CODEX_ACCESS_TOKEN`
- `ANTHROPIC_API_KEY`

After a credential is configured, updating or manually dispatching `.github/workflows/agent-benchmark.yml` will run Baseline / Minimal ACL / Full ACL for the corresponding agent.

## Evidence rule

This blocked run must not be counted as a benchmark result.

The first publishable Input Track result requires actual model execution and committed raw/aggregate results.


## Retry after OPENAI_API_KEY fallback support

Workflow run: 37797545467

Commit: `f9e8d828fe59038d3af5649b784a05d3b6b83005`

Observed:

- Codex credential gate: no `CODEX_ACCESS_TOKEN` and no `OPENAI_API_KEY`; agent execution skipped.
- Claude credential gate: no `ANTHROPIC_API_KEY`; agent execution skipped.
- No model outputs were produced.
- No A/B result can be inferred from this run.

Current blocker is exclusively repository credential configuration; the smoke workflow path itself is functioning.


## Ablation infrastructure

Status: **implemented / self-tested / not executed on real models**

The ablation manifest contains:

- full
- full_minus_action
- full_minus_reference
- full_minus_constraint
- full_minus_flow
- full_minus_validation

A CI smoke test executed 6 tasks × 6 variants = 36 deterministic reference-agent runs through the same benchmark runner.

Workflow run: 37799769504

Result: **PASS**

The ablation variants preserve underlying task information and remove only the controlled-expression mechanism associated with one rule family.

Real-model ablation remains gated on a meaningful Baseline / Minimal / Full signal.


## Zero-API web-manual track

Status: **implemented / self-tested / ready for browser trials**

Purpose: support Input Track experiments when paid API access is unavailable.

Pipeline:

1. export each task + relevant source files + one prompt variant;
2. run it in a fresh browser chat;
3. preserve the first raw response exactly;
4. require unified diff output;
5. apply the raw diff to a fresh fixture;
6. score with the same visible tests, hidden oracle, forbidden-path and unrequested-change checks.

CI run: 37875494185

Result: **PASS**

Evidence boundary: this track measures first-shot browser model patch generation. It must remain separate from CLI/autonomous-agent results.
