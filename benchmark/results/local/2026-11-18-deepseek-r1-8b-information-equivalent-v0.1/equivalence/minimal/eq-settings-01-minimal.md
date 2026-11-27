# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
完成任务。
事实：
[eq-settings-01/F01] build_settings(settings) 保持单参数公开签名。
[eq-settings-01/F02] 返回一个新 dict，而不是传入对象本身。
[eq-settings-01/F03] 空 settings 的默认值为 mode='viewer' 且 page=1。
[eq-settings-01/F04] settings 中出现的键覆盖同名默认值，未出现的默认键保留。
[eq-settings-01/F05] 不得原地修改传入的 settings。
范围：
[eq-settings-01/S1] 只允许修改 src/session_settings.py；其他所有工作区文件必须保持不变。
评估：
[eq-settings-01/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，不要声称自己运行了测试。

## Workspace files

SOURCE FILE: src/session_settings.py
BEGIN SOURCE
def build_settings(settings):
    return settings
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
