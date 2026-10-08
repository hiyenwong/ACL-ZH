# ACL-ZH Benchmark

ACL-ZH Benchmark 用于回答一个核心问题：

> 与自然中文指令相比，ACL-ZH 是否能让 coding agent 更可靠地完成任务？

Benchmark **不以语言规则命中率作为最终成功标准**。语言指标只用于解释 prompt 差异；最终结论必须来自 agent 的实际行为。

## 三组对照

每个任务至少包含三种 prompt：

1. **Baseline** — 自然中文，保留常见的人类表达方式。
2. **Minimal ACL** — 只消除会影响执行的关键歧义，不强制完整模板。
3. **Full ACL** — 使用当前 ACL-ZH 的完整结构：目标、范围、任务、约束、验证、停止条件。

三组表达应保持相同的任务意图。不得在 ACL 组偷偷增加 Baseline 原本没有的业务要求。

## 主指标

以下指标决定 ACL-ZH 是否有效：

- Task Success Rate ↑
- First-pass Success Rate ↑
- Constraint Violation Rate ↓
- Unrequested Change Rate ↓
- Wrong-file Modification Rate ↓

## 成本指标

这些指标用于判断收益是否值得：

- Input / output tokens ↓
- Tool calls ↓
- Elapsed time ↓
- Diff size
- Prompt length

## 为什么加入 Minimal ACL

第一轮静态测试发现 Full ACL 的平均中文字符数约为 Baseline 的 3.28 倍。

因此只比较 Baseline 与 Full ACL 不够。即使 Full ACL 更好，也无法判断收益来自：

- 受控语言规则；
- 更长的 prompt；
- 更明确的任务说明；
- 或完整模板本身。

Minimal ACL 是必要的控制组。若 Minimal ACL 与 Full ACL 效果相当，应优先保留更短的版本。

## 实验流程

```text
task fixture
   │
   ├── Baseline
   ├── Minimal ACL
   └── Full ACL
          │
          ▼
same agent / same model / same reasoning level
          │
          ▼
fresh workspace for every run
          │
          ▼
tests + diff scorer + constraint scorer
          │
          ▼
raw JSONL result
          │
          ▼
aggregate.py
```

## 运行

Benchmark runner 不绑定某一个 agent CLI。通过命令模板调用 agent：

```bash
python benchmark/agent-eval/run.py \
  --manifest benchmark/tasks/manifest.jsonl \
  --variant baseline \
  --agent codex \
  --agent-command 'codex exec "$(cat {prompt_file})"' \
  --repetitions 5
```

Claude Code 也使用相同 harness，只替换 `--agent-command`。请记录真实 CLI 版本和完整命令。

> Codex 官方将 `codex exec` 定位为非交互式自动化入口。具体 CLI flags 可能随版本变化，因此 benchmark 记录实际命令，而不是把易变化的 flags 固化进规范。

## 结果聚合

```bash
python benchmark/agent-eval/aggregate.py benchmark/results/agent/*.jsonl
```

## 当前证据状态

- 静态语言比较：**已执行**
- coding agent 行为 A/B：**尚未执行**
- rule-family ablation：**尚未执行**

在真实 agent A/B 完成前，不应声称 ACL-ZH 能提高 coding agent 成功率。

详细实验规范见 [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md)。
