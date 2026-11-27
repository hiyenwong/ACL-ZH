# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：让 normalize_options() 不修改调用方输入。
任务：返回 options 的新 dict，并把新 dict 中的 mode 转成小写。
约束：不得原地修改传入的 options。返回对象必须与输入对象不是同一个 dict。
验证：运行 python -m unittest discover -s tests。

## Workspace files

SOURCE FILE: src/options.py
BEGIN SOURCE
def normalize_options(options):
    if 'mode' in options:
        options['mode'] = str(options['mode']).lower()
    return options
END SOURCE

SOURCE FILE: tests/test_options.py
BEGIN SOURCE
import unittest
from src.options import normalize_options
class T(unittest.TestCase):
 def test_result(self): self.assertEqual(normalize_options({'mode':'FAST'})['mode'],'fast')
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
