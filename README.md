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

## Benchmark 设计

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

## 当前实验结果

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

### 3. 真实 Claude Code / Codex A/B：尚未执行

**目前仍然没有证据证明 ACL-ZH 能提高 Claude Code、Codex 或其他 coding agent 的真实任务成功率。**

正式结论必须来自相同模型、相同 reasoning level、相同起始代码、相同权限和相同测试条件下的 Baseline / Minimal ACL / Full ACL 对照。

结果状态见 [benchmark/results/README.md](benchmark/results/README.md)。

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
- 后续 rule-family ablation 设计。

runner 不绑定某一个 coding-agent CLI，通过命令模板调用。Codex 官方支持 `codex exec` 与 JSONL event stream；Claude Code 官方支持 `claude -p` 非交互模式和 JSON 输出。实际 benchmark 必须记录模型、CLI 版本、reasoning effort 和完整命令。参考：[Codex evals](https://developers.openai.com/blog/eval-skills/)、[Codex access tokens](https://developers.openai.com/zh-Hans/docs/enterprise/access-tokens) 与 [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)。

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

**v0.2 Experimental — benchmark harness implemented, hardened and self-tested; real-agent workflow ready; downstream ACL effect unvalidated**

## Disclaimer

ACL-ZH is an independent project inspired by the principles of ASD-STE100. It is not affiliated with, endorsed by, or an official derivative of ASD or the Simplified Technical English Maintenance Group (STEMG).

## License

MIT License. See [LICENSE](LICENSE).
