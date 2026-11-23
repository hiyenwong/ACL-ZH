# Preregistration: nanochat reasoning-suppression study v0.1

Prereg ID: `prereg-nanochat-suppression-v0.1`
Date: 2026-11-21
Status: **frozen before any nanochat SFT or evaluation run**
Parent condition: information-equivalent edit-content v0.1
(`c7ab1518-ab20-472c-8c6e-fcf67bf71206`), where all five failures were
hidden-reasoning budget exhaustions and `reasoning_effort` could not suppress
them.

## 1. Why this study exists

The previous run could not separate ACL structure from a decoding artefact:
every failure was a truncation inside an opaque reasoning channel, and the
endpoint accepted `reasoning_effort: none` while continuing to spend the whole
budget on hidden tokens. That makes two questions unanswerable on the LM Studio
model:

1. Is "suppression" even a behavior we can observe, or only a server-side flag?
2. If a model *is* trained to show work, what does asking it to stop showing
   work actually cost in accuracy?

The nanochat stack answers both structurally: its chat template has a single
visible assistant channel (`<|assistant_start|>` … `<|assistant_end|>`), every
sampled token is supervised and counted, and nothing can be hidden behind an
API field. "Suppression" therefore becomes a measurable property of the emitted
token sequence.

This is a mechanism study on a small controlled task. It is **not** an ACL-ZH
effectiveness test and makes no claim about the ACL rule set.

## 2. Fixed environment

- nanochat `github.com/karpathy/nanochat` at commit `92d63d4` (shallow clone),
  `uv sync --extra cpu`, torch 2.9.1, PyTorch MPS backend, Apple M5 Max /
  128 GB. One local edit, vendored as
  `benchmark/local-model/nanochat/0001-external-sft-mixture.patch`: when
  `NANOCHAT_SFT_TASKS` is set, `scripts/chat_sft.py` takes its train mixture and
  validation set from that module instead of SmolTalk/MMLU/GSM8K.
- Tokenizer: `scripts.tok_train --max-chars=2000000000` on 8 ClimbMix shards,
  the shipped `runs/runcpu.sh` configuration.
- Base model: `runs/runcpu.sh` settings, `--depth=6 --head-dim=64
  --window-pattern=L --max-seq-len=512 --device-batch-size=32
  --total-batch-size=16384 --num-iterations=5000`, tag `d6-supp`. Base eval and
  sampling disabled except the periodic loss eval.
- SFT: `scripts.chat_sft --num-iterations=1500`, batch settings inherited from
  the base checkpoint, ChatCORE and loss eval disabled
  (`--eval-every=-1 --chatcore-every=-1`). Both arms start from the same base
  checkpoint and optimizer state.

## 3. Task and treatment

Synthetic two-operand addition, generated deterministically
(`benchmark/local-model/nanochat/suppression_arith.py`):

- 24,000 training items, seed 20261121; 200 held-out evaluation items, seed
  771721. Half single-digit pairs, half pairs with at least one operand ≥ 10.
- Each item carries one of two instruction phrasings, alternating by index:
  - trace instruction: `Compute a+b. Show your work, then give the final answer.`
  - direct instruction: `Compute a+b. Do not show your work. Give only the final answer.`
- Targets:
  - trace target: a four-line decimal decomposition of `a+b`, then `Answer: N`;
  - direct target: `Answer: N`.

Arms (identical items, identical prompt text, identical order; only targets
differ):

| Arm | model tag | trace-instruction target | direct-instruction target |
|---|---|---|---|
| T (trace-trained) | `d6-supp-trace` | trace | direct |
| D (direct-trained) | `d6-supp-direct` | direct | direct |

Arm D never sees a decomposition; arm T sees one on half of its examples.

## 4. Evaluation

Frozen prompt set written by
`python -m suppression_arith --write-eval-set <path>`: 200 items × both
instruction modes = 400 prompts per arm. Greedy decoding
(`temperature=0`, `max_tokens=160`) through nanochat's `Engine`.

Recorded per generation: full text, parsed final integer, correctness,
generated token count, characters before `Answer:` (visible work),
number of non-empty lines before `Answer:`, presence of an `a + b =` step
pattern, and whether generation terminated with `<|assistant_end|>`.

Primary endpoints (reported per arm, never pooled across instruction modes):

1. **direct-mode accuracy** — the suppression condition for both arms;
2. **trace leakage under the direct instruction** — share of direct-mode
   generations that emit non-empty visible work before the answer
   (`prefix_chars > 0`);
3. **trace-mode accuracy** — for comparison with the visible-work condition;
4. mean visible work (`prefix_chars`, `prefix_lines`) per mode.

## 5. Predefined interpretation

- The study answers "what does suppression cost", not "does suppression work":
  a model cannot hide tokens in this stack, so any reduction in visible work is
  either shorter emitted text or accuracy loss.
- Arm comparison is **compute-matched** (equal SFT tokens per iteration and
  equal iteration count), not example-matched. Arm T's targets are longer, so
  it sees fewer distinct examples per fixed token budget. This confound is
  stated wherever T is compared with D, and no "trace training improves
  reasoning" claim is made from this run alone.
- Secondary: example-count exposure per arm is reported from token-length
  accounting, and an example-matched follow-up (arm D trained for proportionally
  more iterations) is specified but not run here.

## 5A. Amendment A1 (2026-11-21, before the primary comparison)

**Step budget.** `scripts/chat_sft.py` ends training when its conversation
dataloader finishes the first epoch (`last_step`), so the frozen
`--num-iterations=1500` is unreachable with a 24,000-item mixture: the direct
arm stops at 40 steps and the trace arm at 62 steps (longer targets pack fewer
conversations per row, so the epoch is longer). A pilot pair at those unequal
lengths was run first and is reported only as exploratory.

**Frozen comparison.** The primary pair uses an equal optimization budget of
**40 steps per arm** (`--num-iterations=40`), i.e. 40 × 16,384 = 655,360 SFT
tokens per arm, tags `d6-supp-trace-eq40` and `d6-supp-direct-eq40`. Equal
steps, equal tokens, identical items and prompts; only the targets differ.

**Known residual confound.** At equal steps the trace arm still consumes more
tokens per conversation, so it sees fewer distinct examples (estimated from the
mean tokens per conversation, reported with the results). No example-matched
arm is run here.

**Implementation note.** `chat_sft.py` uses one `--model-tag` for both loading
the base checkpoint and saving the SFT checkpoint, so the base directory was
copied to per-arm tags before each run. No training code changed.

## 5B. Amendment A2 (2026-11-23, before the d12 runs)

**Escalation arm.** Following the d6 equal-budget and pilot runs, the protocol
is applied to the next size of the nanochat miniseries, `--depth=12`
(`model_dim = 12 * 64 = 768`), same tokenizer, same base-train settings and
5000 iterations, tag `d12-supp`. Same synthetic task, same items, same arms,
same greedy evaluation.

**Step budget at d12.** Primary condition: each arm is trained for **one full
epoch of the same 24,000 items** (steps differ between arms, as at d6). This is
the example-matched condition; the equal-token 40-step condition from A1 is
kept only for cross-model comparability if both d12 epochs finish within one
hour of training time each, and is otherwise dropped.

**Analysis addition.** For silent multi-digit failures, report the mean
absolute numeric distance `|predicted - answer|` per arm as a descriptive
error-magnitude measure. No other new endpoints.

## 6. Predefined gates and failure categories
- **Learnability gate** (checked first): if direct-mode accuracy for both arms
  is below 0.50 on the single-digit subset, d6 is treated as a capability floor
  for this task. The suppression measurements are still reported, but no
  arm-difference interpretation is offered and the documented escalation is a
  deeper base model (`--depth=12`) with the same protocol.
- **Ceiling gate**: if direct-mode accuracy is ≥ 0.98 for both arms, the task
  is saturated; the suppression endpoints are reported as ceiling-limited.
- Failure categories per generation: `correct`, `wrong_value`,
  `no_answer_field`, `truncated` (hit `max_tokens` without
  `<|assistant_end|>`).

## 7. Deviations

Any change to the frozen settings above is recorded as a dated amendment
before the affected run, with the reason. Exploration outside this protocol
(e.g. the LM Studio endpoint probe in
`artifacts/reasoning-suppression-probe/`) is reported as exploratory and never
merged into these endpoints.
