# ACL-ZH Instructions for Claude Code

Use ACL-ZH for plans, technical instructions, change summaries, and other execution-oriented Chinese text.

Source of truth:
- ../../spec/ACL-ZH-000.md
- ../../rules/rules.yaml
- ../../rules/ambiguous-words.yaml

Requirements:
- Use one primary action per instruction.
- Name the action object.
- Separate tasks from constraints.
- Avoid ambiguous references and undefined degree words.
- State conditions before dependent actions.
- State stop conditions when ambiguity, risk, or scope conflicts exist.
- Do not change code identifiers only to satisfy language rules.
- Do not claim completion without validation evidence.

Before reporting completion:
1. Run the project validation commands that are available.
2. Report the commands and results.
3. Report unresolved issues.
