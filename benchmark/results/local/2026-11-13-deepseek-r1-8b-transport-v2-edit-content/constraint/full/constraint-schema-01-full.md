# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：压缩 payload。
任务：修改 src/payload.py 的 compact_payload()，返回不包含 None 值字段的新 dict。
约束：不得修改 schema.json。不得删除值为 0、False 或空字符串的字段。
验证：运行 python -m unittest discover -s tests。

## Workspace files

SOURCE FILE: schema.json
BEGIN SOURCE
{"type":"object"}
END SOURCE

SOURCE FILE: src/payload.py
BEGIN SOURCE
def compact_payload(value):
    return dict(value)
END SOURCE

SOURCE FILE: tests/test_payload.py
BEGIN SOURCE
import unittest
from src.payload import compact_payload
class T(unittest.TestCase):
 def test_copy(self): self.assertEqual(compact_payload({'a':1}),{'a':1})
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
