# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：实现稳定的 SHA-256 文本摘要。
任务：修改 src/hashutil.py 的 sha256_text()，返回 UTF-8 输入的 SHA-256 十六进制字符串。
约束：只能使用 Python 标准库。不得新增第三方依赖。不得修改 requirements.txt。
验证：运行 python -m unittest discover -s tests。

## Workspace files

SOURCE FILE: requirements.txt
BEGIN SOURCE

END SOURCE

SOURCE FILE: src/hashutil.py
BEGIN SOURCE
def sha256_text(value):
    return value
END SOURCE

SOURCE FILE: tests/test_hashutil.py
BEGIN SOURCE
import unittest
from src.hashutil import sha256_text
class T(unittest.TestCase):
 def test_callable(self): self.assertTrue(callable(sha256_text))
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
