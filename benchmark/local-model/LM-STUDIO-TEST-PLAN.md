# Local Model Test Protocol (LM Studio)

Status: v0.1 protocol for reproducible local testing

This document defines the rules for running ACL-ZH input benchmarks on a local machine. LM Studio is a first-class supported path.

The goal is not to maximize benchmark scores. The goal is to make local results reproducible, auditable, and comparable with repository results.

## 1. Evidence boundary

A local run is evidence about the exact tested combination of:

- model and model build;
- quantization;
- prompt/task manifest commit;
- ACL-ZH specification commit;
- decoding parameters;
- context length/runtime;
- scorer version.

Do not generalize one local run to "ACL-ZH works" or "ACL-ZH does not work".

Primary task success remains:

`patch applies && visible tests pass && hidden oracle passes && no constraint violation`.

Patch-apply rate is a separate format/compliance metric. It is not task success.

## 2. Mandatory test rules

### R1 — One model per experiment

Do not switch model files, quantization, context length, or inference backend inside one experiment.

Record the exact LM Studio model identifier and quantization.

### R2 — Fresh request for every run

Each task/variant must be a new stateless Chat Completions request.

Do not carry chat history between runs. Do not retry or repair a response in the same scored repetition.

### R3 — Preserve raw first response

Save the assistant response exactly as returned.

Do not remove Markdown fences, prose, whitespace, or malformed diff text before strict scoring.

Fence-only normalization is allowed only as a separately labeled diagnostic score.

### R4 — Fixed decoding

Default local protocol:

- temperature: 0
- top_p: 1
- seed: 20261011
- max_tokens: 256

If the model/runtime does not honor a parameter, record that fact.

Changing any decoding parameter creates a different experiment.

### R5 — Fixed prompt source

Prompts must be generated from the committed task manifest with
`benchmark/web-eval/export_web_prompts.py`.

Do not hand-edit generated prompts.

### R6 — No manual intervention

During scored runs:

- do not edit model output;
- do not ask follow-up questions;
- do not paste compiler/test errors back to the model;
- do not manually repair patches;
- do not change workspace files.

Manual analysis is allowed only after raw responses are archived.

### R7 — Strict score is primary

Primary score uses the raw model response and `score_web_patch.py`.

Secondary diagnostics may include:

- fence-only normalized patch apply;
- semantic/content review;
- error classification.

Never merge diagnostic scores into primary task-success counts.

### R8 — Record environment metadata

Every experiment must record at least:

- date/time;
- git commit SHA;
- OS;
- CPU/GPU/Apple Silicon;
- RAM;
- LM Studio version;
- model identifier;
- quantization;
- context length if known;
- base URL;
- decoding parameters;
- experiment file;
- manifest file.

### R9 — Deterministic repeats

If temperature=0 and a fixed seed/runtime produce identical output, repeating the exact same run is not independent evidence.

For additional evidence, prefer:

- additional tasks;
- another named model;
- another model size;
- a deliberately declared seed/sampling study.

### R10 — Promote results only after review

Local outputs should first live outside committed benchmark conclusions.

Before promoting results into `benchmark/results/` or the top-level README:

1. preserve raw outputs;
2. run strict scoring;
3. run diagnostic scoring;
4. inspect suspicious successes/failures;
5. verify environment metadata;
6. commit a result report with an explicit evidence boundary.

## 3. Recommended local test phases

### Phase A — Dependency mirror diagnostic

Use:

- experiment: `benchmark/local-model/experiment-qwen25-coder-3b-dependency-mirror-v0.4.json`
- manifest: `benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl`

Runs: 4 tasks × 3 variants = 12.

Purpose: test whether the previous `dependency-01` behavior survives controlled prompt-structure changes.

Do not treat this as a general ACL effectiveness test.

### Phase B — Constraint-focused replication

Use:

- experiment: `benchmark/local-model/experiment-qwen25-coder-3b-constraint-v0.3.json`
- manifest: `benchmark/tasks/manifest-constraint-v0.3.jsonl`

Runs: 12 tasks × 3 variants = 36.

Purpose: test whether any effect generalizes across constraint tasks.

### Phase C — Expanded benchmark

Use the 12-task expanded manifest and the corresponding fixed experiment.

Purpose: compare behavior across multiple task families.

Only proceed after Phase A/B tooling and scoring are verified locally.

## 4. LM Studio setup

Start LM Studio's local server from the Developer tab.

The repository runner defaults to:

`http://127.0.0.1:1234/v1`

Check available model identifiers:

```bash
curl http://127.0.0.1:1234/v1/models
```

Use the exact model identifier returned by LM Studio.

## 5. Run a local LM Studio experiment

Example:

```bash
python benchmark/local-model/run_lm_studio.py \
  --base-url http://127.0.0.1:1234/v1 \
  --model "YOUR_LM_STUDIO_MODEL_ID" \
  --experiment benchmark/local-model/experiment-qwen25-coder-3b-dependency-mirror-v0.4.json \
  --manifest benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl \
  --workdir benchmark/results/local/manual-lmstudio-dependency-mirror \
  --temperature 0 \
  --top-p 1 \
  --seed 20261011 \
  --max-tokens 256
```

The runner stores:

- generated prompt bundles;
- run manifest;
- every raw response;
- request metadata;
- environment metadata.

## 6. Score the run

```bash
python benchmark/local-model/score_lm_studio_run.py \
  --workdir benchmark/results/local/manual-lmstudio-dependency-mirror \
  --experiment benchmark/local-model/experiment-qwen25-coder-3b-dependency-mirror-v0.4.json \
  --manifest benchmark/tasks/manifest-dependency-mirror-v0.4.jsonl
```

Outputs:

- `results-strict.jsonl`
- `results-normalized.jsonl`
- `aggregate.json`

## 7. Minimum result report

When reporting a local result, include:

```text
Model:
Quantization:
LM Studio version:
Hardware:
Experiment:
Manifest:
Git commit:
Temperature:
Top-p:
Seed:
Max tokens:

Baseline task success: X/N
Minimal task success: X/N
Full task success: X/N

Baseline patch apply: X/N
Minimal patch apply: X/N
Full patch apply: X/N

Normalized diagnostic:
Notable failures:
Evidence boundary:
```

## 8. Interpretation rules

Allowed:

- "Full ACL had a higher patch-apply rate in this exact local experiment."
- "No variant passed the hidden oracle in this run."
- "This model/runtime showed a serialization floor."
- "This task-specific effect reproduced/did not reproduce."

Not allowed without broader evidence:

- "ACL-ZH improves agents."
- "Full ACL is better."
- "Constraint rules are validated."
- "A model size threshold has been proven."

## 9. Recommended model ladder

For local testing, choose models that comfortably fit the machine and keep the exact model fixed within one experiment.

Recommended order:

1. a ~3B coding/instruct model for tool validation;
2. a ~7B model for a stronger discriminating run;
3. a larger model only if memory and latency remain practical.

Do not compare two different quantizations as if they were the same model condition.

## 10. Result naming

Recommended directory format:

`benchmark/results/local/<date>-<model>-<experiment-id>/`

Do not overwrite an earlier run. Keep raw outputs immutable.
