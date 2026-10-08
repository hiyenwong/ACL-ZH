# ACL-ZH

**Agent Controlled Language for Chinese**

ACL-ZH 是一个研究型项目：探索“受控中文指令”是否能提高 AI Agent 的执行可靠性。项目受 **ASD-STE100 (Simplified Technical English)** 的受控语言思想启发，但不是 ASD-STE100 的中文翻译、官方扩展或兼容性认证。

核心问题不是“这种写法看起来是否更规范”，而是：

> **同一个任务，在相同模型和环境下，ACL-ZH 是否真的比自然中文带来更高的成功率、更低的约束违反和更少的越界修改？**

## 项目原则

ACL-ZH 当前是 **hypothesis + benchmark**，不是已经验证有效的标准。

规则只有在实验中证明有价值，或具有明确的安全/正确性理由时，才应该进入稳定规范。没有数据支持的规则可以被修改或删除。

## 与 ASD-STE100 的关系

| ASD-STE100 | ACL-ZH |
| --- | --- |
| Simplified Technical English | Agent Controlled Language for Chinese |
| Human → Human | Human → AI Agent → Action |
| 控制词汇和句法 | 研究词汇、句法、约束、控制流和验证对 Agent 行为的影响 |
| 目标是清晰一致的技术信息 | 目标是可重复、可验证的 Agent 执行 |

ACL-ZH 借鉴 ASD-STE100 的方法论：减少歧义、统一术语、限制容易误解的表达，并尝试把规则变成可检查对象。

## 当前规则草案

v0.1 将规则分为五组：

- **A — Action**：动作原子化和明确对象。
- **R — Reference**：减少模糊指代。
- **C — Constraint**：明确硬约束和修改边界。
- **F — Flow**：显式条件、分支和停止条件。
- **V — Validation**：可验证的完成条件和证据。

详见 [spec/ACL-ZH-000.md](spec/ACL-ZH-000.md)。

## Benchmark：不是只比较“自然中文 vs 长 prompt”

Benchmark 现在定义三组：

1. **Baseline**：自然中文。
2. **Minimal ACL**：只消除关键执行歧义。
3. **Full ACL**：完整 ACL-ZH 结构化表达。

加入 Minimal ACL 是因为第一轮静态测试发现 Full ACL 平均长度约为 Baseline 的 **3.28 倍**。如果不加入中间组，就无法知道收益究竟来自受控语言规则，还是单纯来自“写得更长、更详细”。

主指标全部是 Agent 行为指标：

- Task Success Rate
- First-pass Success Rate
- Constraint Violation Rate
- Unrequested Change Rate
- Wrong-file Modification Rate

Token、tool calls、耗时和 prompt 长度只作为成本指标。

完整设计见 [benchmark/BENCHMARK_SPEC.md](benchmark/BENCHMARK_SPEC.md)。

## 当前实验结果

### 已完成：静态语言对照

12 组 Baseline / Full ACL 文本对照显示：

- Baseline 平均长度：**21.5** 个中文字符；
- Full ACL 平均长度：**70.417** 个中文字符；
- Full ACL 长度约为 Baseline 的 **3.28×**；
- 当前规则定义的模糊表达命中从平均 **1.5** 降至 **0**。

这只能说明 Full ACL 更显式、更长，并减少了我们定义的歧义标记。

### 尚未证明：真实 Agent 性能提升

**目前没有证据证明 ACL-ZH 能提高 Claude Code、Codex 或其他 coding agent 的任务成功率。**

真实 A/B 结果必须在相同模型、相同 reasoning level、相同起始代码、相同权限和相同测试条件下运行后才能得出。

结果状态见 [benchmark/results/README.md](benchmark/results/README.md)。

## 已落地的 Benchmark Harness

仓库已经包含：

```text
benchmark/
├── BENCHMARK_SPEC.md
├── METHODOLOGY.md
├── cases.jsonl
├── tasks/
│   └── manifest.jsonl
├── agent-eval/
│   ├── run.py
│   └── aggregate.py
├── schema/
│   └── result.schema.json
└── results/
    ├── README.md
    └── static-v0.1.json
```

runner 支持任意可非交互执行的 coding-agent CLI，通过命令模板调用。Codex 官方提供 `codex exec` 作为非交互自动化入口；Claude Code 运行时也应记录实际 CLI 版本和完整命令，避免把易变化的参数写死在规范中。

## 下一阶段：真实 Agent A/B + Ablation

当 Baseline / Minimal / Full 三组得到真实结果后，才进入规则消融：

```text
Full ACL
├── remove Action
├── remove Reference
├── remove Constraint
├── remove Flow
└── remove Validation
```

如果移除某一规则组以后表现没有下降，该规则组不能仅凭“感觉合理”成为强制规范。

## Agent 适配

- Claude Code：`adapters/claude-code/CLAUDE.md`
- OpenAI Codex：`adapters/codex/AGENTS.md`

这些 adapter 目前同样属于实验对象，而不是已验证的最佳实践。

## 状态

**v0.2 Experimental — benchmark harness implemented; downstream agent effect unvalidated**

## Disclaimer

ACL-ZH is an independent project inspired by the principles of ASD-STE100. It is not affiliated with, endorsed by, or an official derivative of ASD or the Simplified Technical English Maintenance Group (STEMG).

## License

MIT License. See [LICENSE](LICENSE).
