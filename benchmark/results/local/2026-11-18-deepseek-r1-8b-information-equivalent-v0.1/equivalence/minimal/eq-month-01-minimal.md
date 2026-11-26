# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
完成任务。
事实：
[eq-month-01/F01] month_name(number) 保持单参数公开签名。
[eq-month-01/F02] month_name(1) 返回 'January'。
[eq-month-01/F03] month_name(12) 返回 'December'。
[eq-month-01/F04] number 为 0 或 13 时抛出 InvalidMonthError。
范围：
[eq-month-01/S1] 只允许修改 src/months.py；其他所有工作区文件必须保持不变。
评估：
[eq-month-01/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，不要声称自己运行了测试。

## Workspace files

SOURCE FILE: src/months.py
BEGIN SOURCE
class InvalidMonthError(Exception):
    pass

def month_name(number):
    return str(number)
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
