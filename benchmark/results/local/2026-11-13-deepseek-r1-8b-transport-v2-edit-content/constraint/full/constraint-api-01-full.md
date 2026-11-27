# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：规范 token 空白。
任务：修改 src/token.py 的 normalize_token(token)，去掉首尾空白。
约束：不得修改公开函数签名。返回类型必须保持 str。不得增加额外编码或大小写转换。
验证：运行 python -m unittest discover -s tests。

## Workspace files

SOURCE FILE: src/token.py
BEGIN SOURCE
def normalize_token(token):
    return token
END SOURCE

SOURCE FILE: tests/test_token.py
BEGIN SOURCE
import unittest
from src.token import normalize_token
class T(unittest.TestCase):
 def test_plain(self): self.assertEqual(normalize_token('abc'),'abc')
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
