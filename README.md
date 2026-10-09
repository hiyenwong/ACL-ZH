# ACL-ZH

**Agent Controlled Language for Chinese**

ACL-ZH 是一个研究型项目：探索受控中文是否能降低 Human ↔ Agent 双向通信中的信息损失。第一阶段研究 Human → Agent 的执行可靠性；第二阶段研究 Agent → Human 的解释可理解性。项目受 **ASD-STE100 (Simplified Technical English)** 的受控语言思想启发，但不是 ASD-STE100 的中文翻译、官方扩展或兼容性认证。

核心问题不是“这种写法看起来是否更规范”，而是：

> **同样的信息，用受控中文表达后，Agent 是否执行得更可靠？人类是否理解得更准确、更快？**

## 项目原则

ACL-ZH 当前是 **hypothesis + benchmark**，不是已经验证有效的标准。

规则只有在实验中证明有价值，或具有明确的安全/正确性理由时，才应该进入稳定规范。没有数据支持的规则可以被修改或删除。

## 双向研究框架

ACL-ZH 将 Human–AI communication 拆成两个独立方向：

```text
Human → Agent
Instruction Reliability

Agent → Human
Understanding Efficiency
```

### Input Track — Human → Agent

研究受控中文是否改善：

- Task Success Rate
- First-pass Success Rate
- Constraint Violation Rate
- Unrequested Change Rate
- Wrong-file Modification Rate

### Output Track — Agent → Human

研究受控中文是否改善：

- Comprehension Accuracy
- Time to Correct Answer
- Misinterpretation Rate
- Delayed Recall Accuracy
- Cognitive Load

Output Track 还会单独比较 Diagram、Interactive HTML 等输出模态，但这些结果不能被混同为“受控语言效果”。

详见 [benchmark/output/prose-comprehension/SPEC.md](benchmark/output/prose-comprehension/SPEC.md)。

## 与 ASD-STE100 的关系

| ASD-STE100 | ACL-ZH |
| --- | --- |
| Simplified Technical English | Agent Controlled Language for Chinese |
| Human → Human | Human ↔ AI Agent |
| 控制词汇和句法 | 研究受控中文对 Agent 执行与人类理解的影响 |
| 目标是清晰一致的技术信息 | 目标是降低 Human–Agent 双向通信中的歧义与理解成本 |

ACL-ZH 借鉴 ASD-STE100 的方法论：减少歧义、统一术语、限制容易误解的表达，并尝试把规则变成可检查对象。

## 当前规则草案

v0.1 将规则分为五组：

- **A — Action**：动作原子化和明确对象。
- **R — Reference**：减少模糊指代。
- **C — Constraint**：明确硬约束和修改边界。
- **F — Flow**：显式条件、分支和停止条件。
- **V — Validation**：可验证的完成条件和证据。

详见 [spec/ACL-ZH-000.md](spec/ACL-ZH-000.md)。

## Input Benchmark 设计

Benchmark 不只比较“自然中文 vs 更长的 prompt”，而是三组：

1. **Baseline**：自然中文。
2. **Minimal ACL**：只消除关键执行歧义。
3. **Full ACL**：完整 ACL-ZH 结构化表达。

加入 Minimal ACL 是因为第一轮静态测试发现 Full ACL 平均长度约为 Baseline 的 **3.28 倍**。如果只比较 Baseline 与 Full ACL，就无法判断收益究竟来自受控语言规则，还是单纯来自“写得更长、更详细”。

主指标全部是 Agent 行为指标：

- Task Success Rate
- First-pass Success Rate
- Constraint Violation Rate
- Unrequested Change Rate
- Wrong-file Modification Rate

Token、tool calls、耗时和 prompt 长度只作为成本指标。

完整实验设计见 [benchmark/BENCHMARK_SPEC.md](benchmark/BENCHMARK_SPEC.md)。

## 当前实验结果与证据边界

### 1. 静态语言对照：已完成

12 组 Baseline / Full ACL 文本对照显示：

- Baseline 平均长度：**21.5** 个中文字符；
- Full ACL 平均长度：**70.417** 个中文字符；
- Full ACL 长度约为 Baseline 的 **3.28×**；
- 当前规则定义的模糊表达命中从平均 **1.5** 降至 **0**。

这只能说明 Full ACL 更显式、更长，并减少了我们定义的歧义标记。

### 2. Benchmark scorer 自检：已完成并通过

Benchmark harness 使用两组确定性控制进行自检：

- **No-op control**：不修改任何代码，必须被 hidden oracle 全部判定失败。
- **Reference control**：执行已知正确的最小实现，必须全部判定成功。

GitHub Actions 实际运行结果：

- No-op：**0 / 6 task success**
- Reference agent：**6 / 6 task success**
- Aggregate smoke test：**PASS**

这证明当前 scorer 至少能够区分“什么都没做”和“已知正确实现”，避免了“现有测试本来就通过，因此空操作被误判为成功”的假阳性。

详见 [benchmark/SELFTEST.md](benchmark/SELFTEST.md)。\n\n在 runner 加固后（prompt 移出 workspace、补充未跟踪文件检测、保存 raw traces、记录模型/CLI 元数据），scorer 自检曾因 reference harness 接口变更失败；修复后最新自检重新通过。这个失败也保留在 Actions 历史中，用于说明 CI 确实能够捕获 benchmark 回归。

### 3. 真实 Claude Code / Codex A/B：已触发 smoke，但被凭证阻塞

首次真实 smoke workflow 已经触发，但 Codex 与 Claude 两个 job 都因仓库未配置模型凭证而跳过，没有产生模型输出。Codex 现在支持 `CODEX_ACCESS_TOKEN` 或 `OPENAI_API_KEY`；Claude 需要 `ANTHROPIC_API_KEY`。

**目前仍然没有证据证明 ACL-ZH 能提高 Claude Code、Codex 或其他 coding agent 的真实任务成功率。已经存在真实开源模型数据，但当前 strict-diff 实验发生测量 floor collapse，不能作为 ACL-ZH 正向或负向效果证据。**

正式结论必须来自相同模型、相同 reasoning level、相同起始代码、相同权限和相同测试条件下的 Baseline / Minimal ACL / Full ACL 对照。

执行状态见 [benchmark/results/INPUT-EXECUTION-STATUS.md](benchmark/results/INPUT-EXECUTION-STATUS.md)，结果状态见 [benchmark/results/README.md](benchmark/results/README.md)。

## 已落地成果

当前仓库已经从“语言规范草案”推进为一个可执行的实验项目：

```text
ACL-ZH/
├── spec/
│   └── ACL-ZH-000.md
├── rules/
│   ├── rules.yaml
│   └── ambiguous-words.yaml
├── adapters/
│   ├── claude-code/CLAUDE.md
│   └── codex/AGENTS.md
└── benchmark/
    ├── BENCHMARK_SPEC.md
    ├── METHODOLOGY.md
    ├── SELFTEST.md
    ├── cases.jsonl
    ├── tasks/
    │   └── manifest.jsonl
    ├── agent-eval/
    │   ├── run.py
    │   ├── aggregate.py
    │   └── reference_agent.py
    ├── schema/
    │   └── result.schema.json
    ├── output/
    │   └── prose-comprehension/
    │       ├── SPEC.md
    │       ├── aggregate.py
    │       ├── items/example.json
    │       ├── schema/response.schema.json
    │       ├── blind-review/
    │       │   ├── PROTOCOL.md
    │       │   ├── anonymize.py
    │       │   ├── review.schema.json
    │       │   ├── aggregate_reviews.py
    │       │   ├── build_reviewer_html.py
    │       │   ├── validate_reviews.py
    │       │   ├── COORDINATOR.md
    │       │   └── selftest.py
    │       └── results/README.md
    └── results/
        ├── README.md
        └── static-v0.1.json
```

### 已经具备的能力

- 三组 prompt 对照：Baseline / Minimal ACL / Full ACL；
- fresh workspace 隔离运行；
- visible tests；
- hidden behavioral oracle；
- forbidden-path 检查；
- unrequested-change 检查；
- task success 自动判定；
- 原始 JSONL 结果记录；
- 聚合统计脚本；
- GitHub Actions scorer 自检；
- rule-family ablation prompt matrix：已落地；
- Ablation harness：6 tasks × 6 variants = 36 reference runs，CI PASS；
- Zero-API `web-manual` Input Track：已落地；
- 网页 prompt bundle exporter + raw unified-diff scorer：CI PASS；
- Agent → Human prose-comprehension 实验规范；
- Output 题库 v0.2：10 items / 30 variants / 20 objective questions；
- Information Equivalence Audit v0.1：FAIL，并保留失败记录；
- Information Equivalence Audit v0.2：PASS WITH LIMITATIONS；
- Independent Blind Review Protocol：已落地；
- 匿名 A/B/C review pack 生成器与 answer-key 分离机制：已落地；
- 生产盲审默认使用私密随机 mapping；固定 seed 仅用于 CI 可重复自检；
- 自包含 reviewer HTML 生成器：已落地；
- reviewer JSONL 完整性校验：已落地；
- Blind review end-to-end self-test：PASS；
- Output item-set 自动校验脚本并已接入 CI；
- 人类实验 response schema；
- Comprehension Accuracy / Misinterpretation Rate / Response Time / Delayed Recall 聚合脚本。

runner 不绑定某一个 coding-agent CLI，通过命令模板调用。Codex 官方支持 `codex exec` 与 JSONL event stream；Claude Code 官方支持 `claude -p` 非交互模式和 JSON 输出。实际 benchmark 必须记录模型、CLI 版本、reasoning effort 和完整命令。参考：[Codex evals](https://developers.openai.com/blog/eval-skills/)、[Codex access tokens](https://developers.openai.com/zh-Hans/docs/enterprise/access-tokens) 与 [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)。

## 下一阶段

### Input Track：真实 Agent A/B + Ablation

Codex / Claude Code 的真实 Agent A/B 仍被 GitHub 模型凭证阻塞；不过零 API 的真实开源模型实验已经开始产生数据。Qwen2.5-Coder-0.5B-Instruct 与 1.5B-Instruct 各完成 18 次 Baseline / Minimal / Full 推理，共 36 次真实模型运行。两轮在 strict unified-diff 协议下均出现 0% patch-apply 的 floor effect，因此这些结果不能支持 ACL-ZH 有效或无效的结论。当前正在把格式遵循与语义任务正确性拆成独立指标。针对“不购买 API”的场景，仓库另外加入了 `web-manual` Input Track：把同一 fixture 与 Baseline / Minimal / Full prompt 导出成网页实验单元，要求浏览器模型首答只返回 unified diff，再送回同一 hidden-oracle scorer。该轨道用于测试网页聊天模型，不与拥有文件/终端工具的 autonomous coding agent 结果混合。按照实验门槛，只有 Baseline / Minimal / Full 得到真实正向信号后，才值得消耗模型额度正式执行规则消融：

```text
Full ACL
├── remove Action
├── remove Reference
├── remove Constraint
├── remove Flow
└── remove Validation
```

当前 ablation 定义采用**信息保持**原则：`Full - Constraint` 等变体不会删除底层任务事实，只移除对应规则族的受控表达机制，避免把“缺少信息”误判成“规则族无效”。如果移除某一规则组以后表现没有下降，该规则组不能仅凭“感觉合理”成为强制规范。详见 [benchmark/ABLATION.md](benchmark/ABLATION.md)。

### Output Track：人类理解实验

prose-comprehension 题库已经迭代到 **v0.2**：10 个技术主题、30 份文本版本（Natural / Light ACL / Full ACL）、20 道客观题。题库覆盖 reverse proxy、事务隔离、缓存、认证 Token、数据管道、消息队列、数据库索引、重试、API 兼容性和并发锁。

v0.1 的第一次 Information Equivalence Audit 明确判定 **FAIL**：发现 5 个 item 存在额外解释信息，并发现 Full ACL 部分结构标签可能提示答案类别。修正后生成 v0.2；第二轮内部审计结果为 **PASS WITH LIMITATIONS**。当前 CI 也改为校验 v0.2。需要注意：v0.2 仍只完成内部语义审查，因此只能称为 **human-study candidate**，不能称为 validated instrument。为此仓库已经加入 Independent Blind Review Protocol：第三方 reviewer 只看到 fact sheet 与匿名 A/B/C 文本，不知道 Natural / Light ACL / Full ACL 的真实身份。匿名化工具、浏览器 reviewer UI、response validator 与端到端 CI 自检已经通过。生产盲审默认生成私密随机映射，不把 mapping 写入公开日志；reviewer 只拿到自包含 HTML，coordinator 单独保管 answer key。真正的独立 reviewer 结果仍未产生。

实验将对比 Natural Chinese / Light ACL / Full ACL，并测理解正确率、查找时间、误解率和延迟回忆。这里的 Light ACL 对应一个重要假设：严格程度不一定越高越好，最优点可能位于自然中文与严格受控语言之间。

当前已经达到 **external blind review ready**。下一步门槛是至少两名独立 reviewer 使用匿名 HTML 独立完成 30 个 review cell，并且所有 A/B/C 版本均无 material issue。聚合结果必须在打开 answer key 之前冻结；只有通过这一门槛，才进入 pilot human-comprehension study。

之后再单独扩展 Diagram-first 和 Interactive HTML。Diagram、HTML、Video 属于输出模态研究，必须和纯语言控制效果分开报告。

## Agent 适配

- Claude Code：`adapters/claude-code/CLAUDE.md`
- OpenAI Codex：`adapters/codex/AGENTS.md`

这些 adapter 目前同样属于实验对象，而不是已验证的最佳实践。

## 状态

**v0.3 Experimental — Input harness self-tested; Output item set audited; external blind-review package ready; ACL effects still unvalidated**

## Disclaimer

ACL-ZH is an independent project inspired by the principles of ASD-STE100. It is not affiliated with, endorsed by, or an official derivative of ASD or the Simplified Technical English Maintenance Group (STEMG).

## License

MIT License. See [LICENSE](LICENSE).
