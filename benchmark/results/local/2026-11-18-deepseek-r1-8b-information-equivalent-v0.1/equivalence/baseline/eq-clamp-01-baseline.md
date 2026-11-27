# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
请按下方事实完成任务。
必要事实：
[eq-clamp-01/F01] clamp(value, low, high) 保持三参数公开签名。
[eq-clamp-01/F02] 输入保证 low <= high。
[eq-clamp-01/F03] value 小于 low 时返回 low。
[eq-clamp-01/F04] value 大于 high 时返回 high。
[eq-clamp-01/F05] value 位于闭区间 [low, high] 内时原值返回。
修改范围：
[eq-clamp-01/S1] 只允许修改 src/clamp.py；其他所有工作区文件必须保持不变。
评估方式：
[eq-clamp-01/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，不要声称自己运行了测试。

## Workspace files

SOURCE FILE: src/clamp.py
BEGIN SOURCE
def clamp(value, low, high):
    return value
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
