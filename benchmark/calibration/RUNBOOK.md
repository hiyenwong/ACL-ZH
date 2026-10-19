# M2-01 Local Baseline Calibration Pilot

Status: infrastructure pilot; **not** confirmatory ACL-ZH evidence.
The 12 tasks are reused from historical `manifest-constraint-v0.3.jsonl`, and have already appeared in prior experiments. No independent held-out confirmatory evaluation set is provided here. A GO decision is only readiness to design the next phase, NOT a declaration of M2-01 complete.

## Step 0 — Update and verify

```bash
git pull --ff-only origin main
python benchmark/calibration/validate_pilot.py \
  --manifest benchmark/calibration/manifests/calibration-pilot-v0.1.jsonl \
  --experiment benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.template.json
curl http://127.0.0.1:1234/v1/models
```

Select a locally available **non-forced-reasoning** code/instruct model if possible. Perform a manual non-benchmark toy preflight to confirm the model emits a complete edit-content response without exhausting tokens. Record LM Studio and hardware version; do NOT preflight on the scored task manifest.

## Step 1 — Pin model and budget BEFORE inference

Use the exact model ID listed by `/v1/models` and the quantization/context from LM Studio. Example placeholders must be replaced:

```bash
python benchmark/calibration/prepare_pilot.py \
  --model 'EXACT_MODEL_ID_FROM_LM_STUDIO' \
  --quantization 'EXACT_QUANTIZATION' \
  --context-length 32768 \
  --max-tokens 1024 \
  --reasoning-effort none
python benchmark/calibration/validate_pilot.py \
  --manifest benchmark/calibration/manifests/calibration-pilot-v0.1.jsonl \
  --experiment benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.json
git add benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.json
git commit -m "chore(calibration): preregister local model condition"
git status --porcelain
```

The last command MUST return empty. If your model refuses `reasoning_effort`, pin `--reasoning-effort server-default` instead and omit that argument from the runner command. Do not silently alter budget/model after scoring starts. `--max-tokens 1024` is an example, NOT an empirically certified model budget; set it from toy preflight.

## Step 2 — Local 12-run inference (baseline only)

The run command must exactly match pinned JSON model and decoding. Set `MODEL`, `MAX_TOKENS`, `REASONING_EFFORT`, `QUANTIZATION` and `CONTEXT_LENGTH` to your committed values (the script below reads the experiment so these cannot diverge):

```bash
python benchmark/calibration/run_pilot.py \
  --experiment benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.json \
  --manifest benchmark/calibration/manifests/calibration-pilot-v0.1.jsonl \
  --workdir /tmp/aclzh-m2-01-baseline-pilot
```

Do not reuse an existing workdir; the wrapper will reject it. Never resume or repair individual outputs and present them as independent first answers.

## Step 3 — Score and gate

```bash
python benchmark/local-model/score_edit_content_run.py \
  --workdir /tmp/aclzh-m2-01-baseline-pilot \
  --experiment benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.json \
  --manifest benchmark/calibration/manifests/calibration-pilot-v0.1.jsonl

python benchmark/calibration/report_pilot.py \
  --workdir /tmp/aclzh-m2-01-baseline-pilot \
  --experiment benchmark/calibration/experiments/experiment-baseline-pilot-v0.1.json \
  --manifest benchmark/calibration/manifests/calibration-pilot-v0.1.jsonl \
  --output /tmp/aclzh-m2-01-baseline-pilot/READINESS.json
```

Archive raw responses, run manifest, generation metadata, scored JSONL and the readiness report. **Do not commit raw traces with secrets or personal information.** Prefer review before publishing. If provenance is mismatched, missing or generation metadata is incomplete, the report MUST NOT promote a GO.

## Unresolved M2-01 completion requirements

- Independent calibration vs evaluation manifests and leakage audit are not implemented. Current tasks are already published/historical.
- Full no-op/reference controls for the pilot should be executed in CI before scored runs.
- M2-02 held-out task sample size and statistical plan must be approved in a separate preregistration.
- This pilot must not be pooled with any previous strict-diff or autonomous-agent evidence.
