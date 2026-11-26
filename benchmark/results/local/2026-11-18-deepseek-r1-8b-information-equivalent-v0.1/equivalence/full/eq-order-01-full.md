# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
# 任务
目标：满足全部原子事实。
## 原子事实
[eq-order-01/F01] ordered_tags(values) 保持单参数公开签名。
[eq-order-01/F02] 返回值必须是 list。
[eq-order-01/F03] 删除重复值，只保留每个值第一次出现的顺序。
[eq-order-01/F04] 不得原地修改传入的 values。
## 范围
[eq-order-01/S1] 只允许修改 src/order_tags.py；其他所有工作区文件必须保持不变。
## 评估
[eq-order-01/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，不要声称自己运行了测试。

## Workspace files

SOURCE FILE: src/order_tags.py
BEGIN SOURCE
def ordered_tags(values):
    return values
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
