# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
safe_divide 除零时别炸，返回空值就行，其他错误别乱吞。

## Workspace files

SOURCE FILE: src/safe_math.py
BEGIN SOURCE
def safe_divide(a, b):
    return a / b
END SOURCE

SOURCE FILE: tests/test_safe_math.py
BEGIN SOURCE
import unittest
from src.safe_math import safe_divide
class T(unittest.TestCase):
 def test_normal(self): self.assertEqual(safe_divide(6,3),2)
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
