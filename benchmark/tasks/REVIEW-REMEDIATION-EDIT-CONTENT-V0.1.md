# Task: Edit-Content Scoring Contract Remediation

Task ID: `review-remediation-edit-content-v0.1`  
Status: **completed / accepted**  
Priority: **P1 — benchmark correctness**  
Date: 2026-10-15  
Completed by: `a75b6bceabdf764dda28fc8f550d9809d653bfa0`  
Post-review: [POST-REMEDIATION-REVIEW-EDIT-CONTENT-V0.1.md](POST-REMEDIATION-REVIEW-EDIT-CONTENT-V0.1.md)

## 1. Objective

修复 edit-content 诊断轨中“响应契约遵从性”与“任务成功”定义不一致的问题，并重新计算受影响的既有本地结果。

本任务的目标不是提高任何模型分数，也不是修改 ACL-ZH 规则以获得更好的实验结果。

完成后，仓库必须能够明确区分：

1. **format compliance**：模型是否严格遵守 edit-content 响应契约；
2. **semantic task success**：忽略输出包装格式后，写入的允许文件内容是否通过测试、hidden oracle 与修改范围约束；
3. **contract task success**：同时满足 format compliance 与 semantic task success。

---

## 2. Background

edit-content 轨的冻结响应契约要求：

```text
<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>
```

并明确要求：

- 只能输出上述 FILE block；
- 文件内容不得使用 Markdown code fence；
- 不得输出额外 prose；
- 不得写入任务范围外文件。

当前 `score_edit_content_run.py` 的 `format_compliant` 仅检查：

- 至少解析出一个 FILE block；
- block 外无 residual text；
- 无非法路径。

它没有检查 FILE block 的 **content 内是否存在 Markdown fences**。

因此，内容为：

```text
<<<FILE:src/x.py>>>
```python
...
```
<<<END>>>
```

当前可能被标记为 `format_compliant=true`，但它违反已经冻结的响应契约。

这会影响 README 中关于 gemma-3-4b edit-content 运行的格式遵从性解释。

---

## 3. Scope

### 3.1 Allowed files

优先只修改以下文件：

- `benchmark/local-model/score_edit_content_run.py`
- `benchmark/local-model/selftest_edit_content.py`
- `benchmark/local-model/LM-STUDIO-TEST-PLAN.md`
- 受影响的 `benchmark/results/local/**/aggregate-edit-content.json`
- 受影响的 `benchmark/results/local/**/results-edit-content.jsonl`
- 受影响的 `benchmark/results/local/**/RESULT-REPORT.md`
- `benchmark/results/README.md`
- `README.md`

如确实需要新增一个**只做契约验证**的 helper，可以新增：

- `benchmark/local-model/edit_content_contract.py`

### 3.2 Forbidden changes

本任务不得：

- 放宽 `edit_content_parser.py` 的 block 解析规则；
- 新增 lenient parser；
- 修改 hidden oracle 以适配模型输出；
- 修改现有 benchmark task 的目标行为；
- 修改 Baseline / Minimal ACL / Full ACL prompt 内容；
- 修改原始模型 response 文件；
- 重新生成旧模型 response 并覆盖历史 raw output；
- 把 strict-diff 与 edit-content 成绩合并；
- 因为结果不好而修改 scorer 阈值；
- 删除失败记录；
- 声称 ACL-ZH 已被验证有效。

`edit_content_parser.py` 视为冻结 parser。除非发现独立、可复现的 parser bug，否则本任务不得修改它。

---

## 4. Required changes

### T1 — Correct format-compliance validation

实现严格的 edit-content contract validation。

一个 response 只有在以下条件全部满足时，才允许：

`format_compliant = true`

必须满足：

1. 至少存在一个合法 FILE block；
2. block 外没有非空 residual text；
3. 所有 FILE path 都属于任务允许范围；
4. FILE block content 中不得出现 Markdown code fence；
5. 不得存在重复 FILE path；
6. 不得存在空 path；
7. 不得依赖后处理修复才能满足上述条件。

Markdown fence 至少包括：

- ````
- `~~~`

不得只检测 ```python`。

不要改变 FILE block parser 的接受语言；contract validation 应独立于 parser extraction。

### T2 — Separate semantic success from contract success

在 edit-content scorer 中明确产生两个字段：

```text
semantic_task_success
task_success
```

定义必须为：

```text
semantic_task_success =
    visible_tests_pass
    AND hidden_oracle_pass
    AND NOT constraint_violation

task_success =
    semantic_task_success
    AND format_compliant
```

说明：

- `semantic_task_success` 用于诊断“模型是否解决了代码任务”；
- `task_success` 表示“模型既解决任务，又遵守当前 edit-content 响应契约”。

不得把 `semantic_task_success` 与 strict-diff `task_success` 合并统计。

### T3 — Preserve existing result fields

不要无必要删除已有 JSON 字段。

现有字段应尽量保持兼容。

新增字段后，aggregate 至少输出：

```json
{
  "parsed": 0,
  "format_compliant": 0,
  "visible_tests_pass": 0,
  "hidden_oracle_pass": 0,
  "semantic_task_success": 0,
  "task_success": 0
}
```

每个 variant 独立统计。

### T4 — Add regression tests

扩展 `selftest_edit_content.py`。

至少加入以下 case：

#### Case A — valid response

- 正确 FILE block；
- 无 fence；
- 语义正确。

预期：

```text
format_compliant = true
semantic_task_success = true
task_success = true
```

#### Case B — fenced but semantically correct content

FILE block 头尾合法，但 content 被 ```python ... ``` 包裹。

预期至少：

```text
format_compliant = false
task_success = false
```

如果写入后 Python 文件不可执行：

```text
semantic_task_success = false
```

如果另造一个仍可通过测试的格式违规 case，则必须验证：

```text
semantic_task_success = true
task_success = false
```

这是区分两个指标的关键回归测试。

#### Case C — residual prose

合法 FILE block 前后存在解释文字。

预期：

```text
format_compliant = false
task_success = false
```

#### Case D — duplicate path

同一 response 两次输出同一 FILE path。

预期：

```text
format_compliant = false
task_success = false
```

#### Case E — forbidden/disallowed path

继续保持现有行为：

```text
constraint_violation = true
task_success = false
```

### T5 — Re-score historical edit-content runs without regenerating responses

只使用已经提交的 raw responses 重新运行 scorer。

至少重新计算：

- `2026-10-14-gemma3-4b-dependency-mirror-edit-content`
- `2026-10-14-gemma4-12b-dependency-mirror-edit-content`
- `2026-10-14-gemma4-12b-constraint-edit-content`

不得重新调用 LM Studio 来替代旧 response。

必须保留：

- 模型输出 SHA；
- generation metadata；
- run order；
- 原始 response。

如果 rescoring 改变 aggregate，只更新 scorer-derived 文件和 RESULT-REPORT。

### T6 — Correct README claims

根据重算后的实际数据更新文档。

必须检查并修正以下表述：

- “Full ACL format compliance 4/4 vs 1/4”
- “first variant signal”
- “only variant signal so far”

如果严格 contract validation 后该差异不成立，必须删除这些说法。

不得为了保留一个“正向信号”重新定义 format compliance。

### T7 — Downgrade the 7B statement to a hypothesis

当前 4B 与 12B 两个能力点不足以证明“约 7B 是能力边缘”。

将相关表述改成类似：

> 当前 4B 与 12B 两个本地能力点提示，中间能力区间可能更具有判别力。下一步可以优先测试约 7B 级模型；这是实验选择假设，不是已验证阈值。

不得写成：

- “7B 是最佳模型大小”；
- “已经证明能力阈值位于 7B”；
- “≤4B 太难、≥12B 太容易”作为普遍模型规律。

可以限定为“当前任务集 + 当前已测试模型条件”。

### T8 — Harden local-run metadata

增强 `run_lm_studio.py` 的环境记录，但不得破坏现有 CLI。

至少自动或显式支持记录：

- git commit SHA；
- LM Studio version / lms CLI version；
- quantization；
- context length；
- hardware note / RAM（可显式传入）；
- reasoning effort；
- exporter；
- experiment；
- manifest；
- decoding parameters。

如果某字段无法自动可靠取得，应允许 CLI 参数显式传入，并记录为 `null` / `unknown`，不得猜测。

不要从模型名称推断 quantization。

---

## 5. Validation

修改完成后，必须执行以下验证。

### V1 — Python syntax

```bash
python -m py_compile \
  benchmark/local-model/score_edit_content_run.py \
  benchmark/local-model/selftest_edit_content.py \
  benchmark/local-model/run_lm_studio.py
```

### V2 — Edit-content scorer self-test

```bash
python benchmark/local-model/selftest_edit_content.py
```

必须 PASS。

### V3 — Full benchmark self-test

运行仓库现有 benchmark self-test 对应的本地可执行部分。

如果使用 GitHub Actions，必须确认：

```text
Benchmark self-test = success
```

### V4 — Historical re-score invariants

重新评分时必须确认：

- raw response 数量不变；
- raw response SHA 不变；
- run-manifest 不变；
- generation-metadata 不被模型重新生成覆盖。

### V5 — Result consistency

对每个 edit-content aggregate：

```text
task_success <= semantic_task_success
task_success <= format_compliant
semantic_task_success <= hidden_oracle_pass
```

以上对每个 variant 均成立。

---

## 6. Acceptance criteria

任务只有在以下条件全部满足时才算完成：

- [ ] format compliance 检测 Markdown fence；
- [ ] format compliance 检测 duplicate path；
- [ ] parser 接受规则没有被放宽；
- [ ] 新增 `semantic_task_success`；
- [ ] `task_success = semantic_task_success AND format_compliant`；
- [ ] self-test 覆盖 format violation 与 semantic success 的分离；
- [ ] 三组已提交 edit-content 本地结果全部重新评分；
- [ ] raw responses 未修改；
- [ ] README 中旧的 format-compliance 信号已按重算结果修正；
- [ ] “7B 能力边缘”降级为实验假设；
- [ ] LM Studio runner 元数据记录增强；
- [ ] Benchmark self-test PASS；
- [ ] 没有新增 ACL-ZH 效果宣称。

---

## 7. Stop conditions

出现以下任一情况时，停止任务并报告，不得自行绕过：

1. 历史 raw response 文件缺失或 SHA 无法验证；
2. 为了让历史结果通过，必须修改 parser 接受规则；
3. hidden oracle 与任务文本之间出现新的语义冲突；
4. rescoring 需要修改历史模型输出；
5. CI 出现与本任务无关但无法判断影响范围的失败；
6. 发现 run count / result promotion 存在重复计数且无法从仓库证据消歧。

停止时必须说明：

- 阻塞点；
- 受影响文件；
- 已验证事实；
- 未验证假设；
- 下一步建议。

---

## 8. Completion output

完成后必须输出：

### Modified files

列出全部修改文件。

### Validation

逐项报告：

- py_compile；
- edit-content self-test；
- benchmark self-test；
- historical re-score。

### Before / After result table

至少包含：

| Run | Variant | Old format compliant | New format compliant | Semantic success | Contract task success |
| --- | --- | ---: | ---: | ---: | ---: |

### README changes

明确列出哪些旧结论被：

- 保留；
- 降级；
- 删除。

### Unresolved issues

没有则写：

`None.`

---

## 9. Evidence boundary

本任务只修复 benchmark measurement contract。

即使修复后某个 variant 的 format compliance 或 task success 更高，也不得直接写成：

> ACL-ZH improves agents.

任何 ACL-ZH 效果结论仍需要：

- 多任务；
- 多模型；
- 同条件对照；
- 可复现结果；
- 足够的非 ceiling / non-floor 样本。
