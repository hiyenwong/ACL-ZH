# nanochat suppression arms

Frozen protocol: `benchmark/local-model/PREREG-NANOCHAT-SUPPRESSION-V0.1.md`.

Layout used on this machine (nanochat is a separate checkout, pinned):

```
<artifacts>/nanochat-src/          # github.com/karpathy/nanochat @ 92d63d4, patched, .venv
<artifacts>/nanochat-artifacts/    # logs, patch, eval set, generations
```

`0001-external-sft-mixture.patch` is the only source change: when
`NANOCHAT_SFT_TASKS` is set, `scripts/chat_sft.py` builds its training mixture
and validation set from that importable module.

## Files here

- `suppression_arith.py` — deterministic addition task, both arms, and the
  frozen evaluation-prompt writer.
- `eval_suppression.py` — greedy generation + exact counting of visible work
  before `Answer:`, run inside the nanochat environment.
- `0001-external-sft-mixture.patch` — the vendored nanochat patch.

## Reproduce

```bash
cd <artifacts>/nanochat-src
uv sync --extra cpu
git apply <this repo>/benchmark/local-model/nanochat/0001-external-sft-mixture.patch

python -m nanochat.dataset -n 8
python -m scripts.tok_train --max-chars=2000000000

python -m scripts.base_train --depth=6 --head-dim=64 --window-pattern=L \
  --max-seq-len=512 --device-batch-size=32 --total-batch-size=16384 \
  --eval-every=100 --eval-tokens=524288 --core-metric-every=-1 \
  --sample-every=100 --num-iterations=5000 --run=dummy --model-tag=d6-supp

export PYTHONPATH=<this repo>/benchmark/local-model/nanochat
python -m suppression_arith --write-eval-set <artifacts>/eval-set.jsonl

for arm in trace direct; do
  NANOCHAT_SUPP_ARM=$arm NANOCHAT_SFT_TASKS=suppression_arith \
  python -m scripts.chat_sft --num-iterations=1500 --eval-every=-1 \
    --chatcore-every=-1 --run=dummy --model-tag=d6-supp-$arm
done

for arm in trace direct; do
  python eval_suppression.py --model-tag d6-supp-$arm \
    --eval-set <artifacts>/eval-set.jsonl --out <artifacts>/eval-$arm.jsonl
done
```
