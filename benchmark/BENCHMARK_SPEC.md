# ACL-ZH Benchmark Specification v0.2

## 1. Research questions

### RQ1
ACL-ZH 是否降低 coding agent 的约束违反率？

### RQ2
ACL-ZH 是否提高任务成功率和首轮成功率？

### RQ3
如果有效，Minimal ACL 是否能以更低 token 成本获得与 Full ACL 接近的收益？

### RQ4
哪些规则族真正产生收益？

- A: Action
- R: Reference
- C: Constraint
- F: Flow
- V: Validation

## 2. Hypotheses

- **H0-1**: Baseline、Minimal ACL、Full ACL 的任务成功率没有显著差异。
- **H0-2**: 三组的约束违反率没有显著差异。
- **H0-3**: Full ACL 相比 Minimal ACL 没有额外行为收益。

只有数据拒绝零假设时，README 才能增加对应的效果声明。

## 3. Experimental arms

### Baseline
自然中文。允许省略、代词、模糊程度词等真实写法，但必须表达相同任务意图。

### Minimal ACL
只修复与行为直接相关的歧义：

- 明确动作对象；
- 明确硬约束；
- 明确必要条件；
- 明确可验证完成标准。

不要求完整章节模板。

### Full ACL
应用当前 ACL-ZH v0.1 的完整结构和规则。

## 4. Fairness rule

三个 arm 必须拥有相同的业务信息。

禁止：

- 只在 ACL arm 中增加新的业务约束；
- 只在 ACL arm 中提供 Baseline 没有的文件名，而这些文件名对完成任务是必要信息；
- 只在 ACL arm 中提供测试命令，而 Baseline 无法从仓库发现该命令；
- 对不同 arm 使用不同起始 commit、依赖状态或权限。

允许：

- 将 Baseline 中隐含但唯一可推断的约束改写为显式约束；
- 将代词替换为 Baseline 上下文中已给出的实体名；
- 将同一信息拆成原子步骤。

## 5. Repetition and order

默认：

- 每个 task × variant 至少 5 次；
- 模型具有明显随机性时建议 10 次；
- 执行顺序随机；
- 每次从干净 fixture 创建新的 workspace；
- 不复用 agent conversation/session。

## 6. Model controls

每组必须记录：

- provider;
- model;
- model version if available;
- CLI version;
- reasoning effort;
- system/project instructions;
- sandbox mode;
- network access;
- approval policy;
- date/time;
- exact command.

不同模型版本不得直接聚合。

## 7. Primary outcome metrics

### Task Success Rate
所有 required checks 通过。

### First-pass Success Rate
agent 第一次结束任务时所有 required checks 即通过，未发生人工纠正或第二轮 prompt。

### Constraint Violation Rate
至少违反一个显式 hard constraint 的 run 比例。

### Unrequested Change Rate
发生任务范围之外语义修改的 run 比例。

### Wrong-file Modification Rate
修改 forbidden path 的 run 比例。

## 8. Secondary metrics

- test pass rate;
- changed files;
- additions/deletions;
- elapsed seconds;
- tool calls;
- input tokens;
- output tokens;
- clarification count;
- agent exit code.

成本指标不能替代质量指标。

## 9. Deterministic scoring

优先采用机器评分：

- unit/integration tests;
- forbidden-path diff checks;
- required-file diff checks;
- exact public API snapshot;
- dependency file checksum;
- command exit status.

只有无法确定性评分的项目才允许人工 review；人工 review 必须 blind to variant。

## 10. Statistical analysis

二元 paired outcomes（同 task、同 repetition seed）优先使用：

- absolute rate difference;
- paired bootstrap confidence interval;
- McNemar test（样本量足够时）。

连续成本指标报告：

- median;
- mean;
- IQR;
- paired delta.

小样本阶段重点报告原始结果和 effect size，不用 p-value 包装不确定结论。

## 11. Decision gates

规则进入稳定规范前至少满足：

1. 在两个以上任务类别中出现正向效果，或有明确安全理由；
2. 不产生明显的任务成功率下降；
3. 成本增量可解释；
4. 通过 rule-family ablation 后仍有独立价值。

未满足的规则保持 experimental，必要时删除。

## 12. Ablation matrix

在 Full ACL 得到正结果后，增加：

- Full - Action
- Full - Reference
- Full - Constraint
- Full - Flow
- Full - Validation

如果删除某规则族后性能不下降，该规则族不能仅凭直觉保留为强制规则。

## 13. Reporting

每次正式 benchmark 发布：

- raw JSONL;
- aggregate JSON;
- environment metadata;
- task manifest commit SHA;
- ACL-ZH spec commit SHA;
-失败案例分析;
- 已知限制。

README 只能引用已经落盘的 benchmark 结果。
