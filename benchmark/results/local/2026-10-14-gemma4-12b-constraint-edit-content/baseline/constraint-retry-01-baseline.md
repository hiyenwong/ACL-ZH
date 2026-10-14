# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
重试逻辑补一下，最多按 attempts 次数试，最后还是失败就把原来的错误抛出去。

## Workspace files

### src/retry.py
```python
def run_with_retry(call, attempts=3):
    return call()
```

### tests/test_retry.py
```python
import unittest
from src.retry import run_with_retry
class T(unittest.TestCase):
 def test_success(self): self.assertEqual(run_with_retry(lambda:'ok'),'ok')
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
