# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：增强 parse_id() 的输入兼容性。
任务：允许 value 是 ID-42 形式或普通数字字符串，并正确解析为整数。
约束：parse_id(value) 的公开签名不得改变。返回类型必须保持 int。不得改变普通数字字符串的既有行为。
验证：运行 python -m unittest discover -s tests。

## Workspace files

SOURCE FILE: src/ids.py
BEGIN SOURCE
def parse_id(value):
    return int(value)
END SOURCE

SOURCE FILE: tests/test_ids.py
BEGIN SOURCE
import unittest
from src.ids import parse_id
class T(unittest.TestCase):
 def test_int(self): self.assertEqual(parse_id('7'),7)
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
