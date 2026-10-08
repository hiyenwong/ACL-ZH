# ACL-ZH v0.1 Draft Specification

## 1. Scope

ACL-ZH is a controlled Chinese instruction language for AI agents. It defines observable instruction-writing rules. It does not define or constrain private model reasoning.

## 2. Normative keywords

- **必须**: mandatory requirement.
- **不得**: prohibited behavior.
- **应该**: expected behavior unless a stated reason prevents it.
- **可以**: optional behavior.

Avoid undefined modal expressions such as “尽量”“最好”“适当”“看情况”“必要时” unless the condition is explicitly defined.

## 3. Rule groups

### A — Action

**ACLZH-A001 — One primary action per instruction**  
一个指令应该只包含一个主要动作。

Bad: 修改 parser 并更新 schema 和测试。  
Good: 修改 parser。更新 schema。更新受影响的测试。

**ACLZH-A002 — State the action object**  
动作必须有明确对象。

**ACLZH-A003 — Prefer executable verbs**  
优先使用可以直接映射到行为的动词，例如“读取、修改、运行、删除、创建、验证、报告”。

**ACLZH-A004 — Separate goal from action**  
目标和执行步骤应该分开表达。

**ACLZH-A005 — Do not hide actions in prose**  
不得把多个执行动作隐藏在长描述中。

### R — Reference

**ACLZH-R001 — Avoid ambiguous pronouns**  
能够使用明确实体名称时，不得使用“这个、那个、它、这里、上面”等模糊指代。

**ACLZH-R002 — Use exact identifiers when available**  
已知文件、函数、接口或模块名称时，应该使用精确标识符。

**ACLZH-R003 — Keep one canonical term per concept**  
同一概念应该使用统一术语。

**ACLZH-R004 — Preserve code identifiers**  
不得为了语言一致性擅自修改代码标识符。

**ACLZH-R005 — Resolve relative references**  
“之前、当前、原来的”等相对表达必须能够从上下文唯一解析。

### C — Constraint

**ACLZH-C001 — Separate constraints from tasks**  
约束必须与任务动作分开表达。

**ACLZH-C002 — Avoid undefined degree words**  
不得使用未定义的“尽量、适当、合理、简单、稍微、顺便”等程度或范围表达。

**ACLZH-C003 — State modification scope**  
涉及修改时，应该明确允许修改和禁止修改的范围。

**ACLZH-C004 — State compatibility requirements explicitly**  
兼容性要求必须明确，例如“不得修改公开 API”。

**ACLZH-C005 — Define exception behavior**  
约束存在例外时，必须说明触发例外的条件和后续行为。

### F — Flow

**ACLZH-F001 — Put conditions before dependent actions**  
条件应该出现在依赖该条件的动作之前。

**ACLZH-F002 — Use explicit branch markers**  
使用“如果 / 否则 / 仅当 / 当”表达分支。

**ACLZH-F003 — Define stop conditions**  
存在高风险、不确定或越权场景时，必须定义停止条件。

**ACLZH-F004 — Do not imply control flow with vague connectors**  
不得仅使用“然后、顺便、同时、看情况”等词隐含控制流。

**ACLZH-F005 — State fallback behavior**  
主要路径失败时，应该说明回退、停止或报告行为。

### V — Validation

**ACLZH-V001 — Define verifiable completion**  
完成条件必须可以被观察或验证。

**ACLZH-V002 — Evidence is required for success claims**  
声明“测试通过”“构建成功”“问题已修复”时，必须有相应验证证据。

**ACLZH-V003 — Name validation commands when known**  
已知验证命令时，应该明确写出命令。

**ACLZH-V004 — Separate execution from validation**  
执行动作和验证动作应该分开。

**ACLZH-V005 — Report unresolved issues**  
任务结束时必须报告未解决的问题或明确说明没有已知未解决问题。

## 4. Recommended instruction structure

```text
目标：
...

范围：
- 允许修改：
- 禁止修改：

任务：
1. ...
2. ...

约束：
- ...

验证：
- ...

停止条件：
- ...

完成输出：
- 修改文件
- 验证结果
- 未解决问题
```

## 5. Design principle

ACL-ZH prioritizes low execution ambiguity over stylistic variety.
