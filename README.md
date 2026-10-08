# ACL-ZH

**Agent Controlled Language for Chinese**

ACL-ZH 是一套面向 AI Agent 的中文受控指令语言规范。项目受 **ASD-STE100 (Simplified Technical English)** 的受控语言思想启发，但不是 ASD-STE100 的中文翻译、官方扩展或兼容性认证。

ACL-ZH 的目标是降低人类向 AI Agent 下达任务时的语言歧义，使执行范围、约束、控制流、停止条件和完成证据更加明确。

> Inspired by ASD-STE100, ACL-ZH defines a controlled Chinese instruction language for reliable and verifiable AI agent execution.

## 核心思想

- 减少同义表达。
- 限制模糊指代。
- 明确动作、对象和范围。
- 区分任务、约束和条件。
- 显式定义停止条件。
- 使用可验证的完成标准。
- 使用项目统一术语。

## 与 ASD-STE100 的关系

| ASD-STE100 | ACL-ZH |
| --- | --- |
| Simplified Technical English | Agent Controlled Language for Chinese |
| Human → Human | Human → AI Agent → Action |
| 控制词汇和句法 | 控制词汇、句法、约束、控制流和验证 |
| 提升技术文档可读性 | 提升 Agent 执行确定性和可验证性 |

## v0.1 规则类别

- **A — Action**：动作必须明确、原子化。
- **R — Reference**：减少模糊指代，明确动作对象。
- **C — Constraint**：约束必须明确，禁止模糊强度。
- **F — Flow**：显式表达条件、分支和停止条件。
- **V — Validation**：完成声明必须有可验证证据。

完整规则见 [spec/ACL-ZH-000.md](spec/ACL-ZH-000.md)。

## 示例

不推荐：

```text
把登录这里优化一下，尽量别改原来的接口，有问题的话把测试也处理一下。
```

推荐：

```text
目标：
重构登录模块。

范围：
- 允许修改：src/auth/**
- 禁止修改：公开 API

任务：
1. 检查现有实现。
2. 识别重复逻辑。
3. 重构重复逻辑。
4. 更新受影响的测试。

约束：
- 不得新增第三方依赖。
- 必须保持现有外部行为。

验证：
- 运行 pnpm lint。
- 运行 pnpm test。
- 运行 pnpm typecheck。

停止条件：
如果完成任务必须修改公开 API，停止并报告原因。
```

## Agent 适配

- Claude Code：`adapters/claude-code/CLAUDE.md`
- OpenAI Codex：`adapters/codex/AGENTS.md`

## 状态

**v0.1 Draft**

## Disclaimer

ACL-ZH is an independent project inspired by the principles of ASD-STE100. It is not affiliated with, endorsed by, or an official derivative of ASD or the Simplified Technical English Maintenance Group (STEMG).

## License

MIT License. See [LICENSE](LICENSE).
