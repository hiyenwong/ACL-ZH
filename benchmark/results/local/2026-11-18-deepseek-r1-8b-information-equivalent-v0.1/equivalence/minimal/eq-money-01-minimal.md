# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
完成任务。
事实：
[eq-money-01/F01] format_amount(cents) 保持单参数公开签名。
[eq-money-01/F02] cents 是非负 int，表示美分数。
[eq-money-01/F03] format_amount(5) 返回 '$0.05'。
[eq-money-01/F04] format_amount(123456) 返回 '$1,234.56'。
[eq-money-01/F05] 返回值必须是 str。
范围：
[eq-money-01/S1] 只允许修改 src/money.py；其他所有工作区文件必须保持不变。
评估：
[eq-money-01/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，不要声称自己运行了测试。

## Workspace files

SOURCE FILE: src/money.py
BEGIN SOURCE
def format_amount(cents):
    return str(cents)
END SOURCE

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.

## Exact output reminder (applies equally to every instruction variant)
The first non-whitespace characters must be <<<FILE: including the literal FILE: prefix.
Each changed file ends with a separate <<<END>>> line.
No explanations, test reports, source delimiters, or Markdown fences before, inside, or after the blocks.
Use real workspace paths. This syntax-only example uses a dummy file; do not output the dummy file:
<<<FILE:example.py>>>
value = 1
<<<END>>>
Now return only the changed workspace file blocks.
