# Result Report: local-gemma4-12b-dependency-mirror-edit-content-v0.4

Run date: 2026-10-14

```text
Model: google/gemma-4-12b-qat
Quantization: Q4_0 (QAT, variant google/gemma-4-12b-qat@q4_0)
LM Studio version: lms CLI commit 69d945a
Hardware: Mac17,6 (Apple Silicon), 128 GB RAM
Experiment: benchmark/local-model/experiment-gemma4-12b-dependency-mirror-edit-content-v0.4.json
Manifest: benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
Git commit at run time: b2e7ffb
Temperature: 0
Top-p: 1
Seed: 20261011
Max tokens: 256
Reasoning effort: none

Baseline: parsed 4/4, format compliant 4/4, tests 4/4, oracle 4/4, semantic success 4/4, task success 4/4
Minimal:  parsed 4/4, format compliant 4/4, tests 4/4, oracle 4/4, semantic success 4/4, task success 4/4
Full:     parsed 4/4, format compliant 4/4, tests 4/4, oracle 4/4, semantic success 4/4, task success 4/4

Metric definitions (remediated scorer, 2026-10-15):
semantic_task_success = visible tests AND hidden oracle AND no
constraint violation; task_success = semantic_task_success AND
format_compliant, where format_compliant now also rejects Markdown
fence lines (``` or ~~~) in block content, duplicate file paths, and
empty paths.

Re-scored 2026-10-15 with the remediated format_compliant detector on
the unchanged raw responses: no count changed (no response contains
fences, duplicates, residual text, or protocol violations).

Notable: all 12 responses are byte-identical (deterministic decoding);
the emitted content is the intended edit in the exact frozen contract
shape.
Evidence boundary: see below.
```

## What this run establishes

Paired with the strict diff-track run of the same model, tasks, and
decoding (`2026-10-11-gemma4-12b-dependency-mirror-v0.4`, 0/12 at
patch apply):

| Track | Baseline | Minimal | Full |
| --- | --- | --- | --- |
| Unified diff (strict) | 0/4 | 0/4 | 0/4 |
| Edit-content (diagnostic) | 4/4 | 4/4 | 4/4 |

For this model on this task family, the strict 0/12 was entirely a
unified-diff serialization failure. Semantic task-solving is 12/12
once the response contract is complete file content.

## Ceiling caveat

All three variants saturate (4/4), so this run shows **no observable
variant separation**. The dependency-mirror tasks are too easy for a
12B-class model once serialization is removed; they cannot
discriminate Baseline / Minimal / Full at this model strength. A
discriminating edit-content experiment needs harder tasks, a weaker
model, or both.

## Evidence boundary

- Diagnostic track (`local-lm-studio-edit-content`). These counts must
  never be merged with strict unified-diff task-success counts.
- The prompt text differs from the diff-track run (response contract
  section), so this is not the same prompt condition.
- Parser was frozen before execution
  (`benchmark/local-model/edit_content_parser.py`); no leniency pass
  exists for this track.
- Allowed: "gemma-4-12b-qat solved all 12 dependency-mirror tasks
  under the file-content contract, with no variant difference."
- Not allowed: any ACL-ZH effectiveness claim (ceiling effect), and
  any comparison against the Qwen2.5-Coder-3B diff-track numbers.

## Provenance hardening re-score (2026-10-18)

Re-scored with the P2-02 provenance-aware scorer on the unchanged raw
responses. The aggregate now records the exact scoring implementation
(`scorer_sha256`, `oracle_sha256`, `parser_sha256`) and the actual input
hashes. This run predates generation-time provenance capture, so the
aggregate is labeled `status: unpinned_baseline`, `score_kind: rescore`.
No count changed; the interpretation above is unaffected.
