# ACL-ZH Instructions for Codex

Apply ACL-ZH to execution-oriented Chinese instructions and reports.

Canonical references:
- ../../spec/ACL-ZH-000.md
- ../../rules/rules.yaml
- ../../rules/ambiguous-words.yaml

Rules:
- Use one primary action per instruction.
- Use explicit action objects.
- Separate goals, tasks, constraints, validation, and stop conditions.
- Avoid ambiguous pronouns when an exact identifier is available.
- Avoid undefined words such as “尽量”“适当”“看情况”.
- Put conditions before dependent actions.
- Preserve code symbols and public API names unless the task explicitly changes them.
- Validate before claiming success.
- Report unresolved issues.
