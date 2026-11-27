# nanochat d12 reasoning-suppression mechanism: completed result

Date: 2026-11-25. Run: `548d036b-3882-49d4-8f57-62f082ac0115`. Source commit: `58ef5bd`.
Preregistration: [`benchmark/local-model/PREREG-NANOCHAT-SUPPRESSION-V0.1.md`](../../../local-model/PREREG-NANOCHAT-SUPPRESSION-V0.1.md).

This is a deterministic synthetic-addition mechanism study on a single-channel nanochat model (every generated token is visible and countable). It is **not** an ACL-ZH effectiveness experiment and supports no ACL claim or general language-model scaling law.

## d12 arms summary (`n = 200` per mode; 101 single-digit, 99 multi-digit)

| Arm | Instruction | Overall accuracy | Single-digit | Multi-digit | Leak rate (visible chars > 0) | Mean generated tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| trace-trained (`d12-supp-trace`) | direct (silent) | 0.690 | 1.000 | 0.3737 | 0.000 | 4.0 |
| trace-trained (`d12-supp-trace`) | trace (visible) | 1.000 | 1.000 | 1.0000 | 1.000 | 33.0 |
| direct-trained (`d12-supp-direct`) | direct (silent) | 0.675 | 1.000 | 0.3434 | 0.000 | 4.0 |
| direct-trained (`d12-supp-direct`) | trace (requested) | 0.660 | 1.000 | 0.3131 | 0.000 | 4.0 |

## Comparison with archived d6 arms (silent direct mode)

| Model / arm | Overall silent accuracy | Multi-digit silent accuracy | Source summary |
| --- | ---: | ---: | --- |
| d6 trace (1 epoch) | 0.615 | 0.2222 | [eval-trace.summary.json](eval-trace.summary.json) |
| d6 direct (1 epoch) | 0.580 | 0.1515 | [eval-direct.summary.json](eval-direct.summary.json) |
| d6 direct-2x | 0.835 | 0.6667 | [eval-direct2x.summary.json](eval-direct2x.summary.json) |
| d12 trace (1 epoch) | 0.690 | 0.3737 | [eval-d12-trace.summary.json](eval-d12-trace.summary.json) |
| d12 direct (1 epoch) | 0.675 | 0.3434 | [eval-d12-direct.summary.json](eval-d12-direct.summary.json) |

## Evidence boundary

- Both d12 arms emitted zero visible work under direct instructions (`leak_rate = 0.000`).
- Depth narrowed the silent multi-digit gap relative to d6 1-epoch arms (`0.2222 -> 0.3737` trace; `0.1515 -> 0.3434` direct), but did not close it (`1.000` visible vs `0.3737` silent).
- Because the d6 direct-2x arm reached `0.6667` silent multi-digit (`0.835` overall silent), exceeding the d12 1-epoch direct arm (`0.3434`), model depth and SFT training budget remain confounded.
- **Post-hoc audit note (added 2026-11-27; archived JSON/JSONL immutable)**: regenerating the historical frozen dataset (`58ef5bd`, `TRAIN_ITEMS = 24000`, `TRAIN_SEED = 20261121`, `EVAL_SEED = 771721`) confirms that using separate random seeds did **not** make train and eval disjoint within the 2,500-pair operand space (2,488 unique pairs appeared in training). Specifically, **199 / 200** evaluation items' operand pairs `(a, b)` occurred in training (`101/101` single-digit, `98/99` multi-digit; `164/165` unique eval pairs), and **389 / 400** evaluation prompts matched training prompts verbatim including instruction mode (`direct` / `trace`). Consequently, the archived d6 and d12 accuracies cannot distinguish arithmetic generalization from memorization of supervised training examples and are retained strictly as historical records. `benchmark/local-model/nanochat/suppression_arith.py` has been updated to partition operand pairs disjointly (`assert not (train_pairs & eval_pairs)`) for any future runs.

## Committed artifacts

- [d12-suppression-report.json](d12-suppression-report.json)
- [eval-d12-trace.summary.json](eval-d12-trace.summary.json) / [eval-d12-trace.jsonl](eval-d12-trace.jsonl)
- [eval-d12-direct.summary.json](eval-d12-direct.summary.json) / [eval-d12-direct.jsonl](eval-d12-direct.jsonl)
- [eval-trace.summary.json](eval-trace.summary.json) / [eval-direct.summary.json](eval-direct.summary.json) / [eval-direct2x.summary.json](eval-direct2x.summary.json)
- [eq40-analysis.json](eq40-analysis.json) / [eval-trace-eq40.summary.json](eval-trace-eq40.summary.json) / [eval-direct-eq40.summary.json](eval-direct-eq40.summary.json)
- [eval-set.jsonl](eval-set.jsonl)
