# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
实现 run_with_retry()：最多调用 call() attempts 次；成功立即返回；连续失败后重新抛出最后一个 ValueError。

## Workspace files

SOURCE FILE: src/retry.py
BEGIN SOURCE
def run_with_retry(call, attempts=3):
    return call()
END SOURCE

SOURCE FILE: tests/test_retry.py
BEGIN SOURCE
import unittest
from src.retry import run_with_retry
class T(unittest.TestCase):
 def test_success(self): self.assertEqual(run_with_retry(lambda:'ok'),'ok')
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
