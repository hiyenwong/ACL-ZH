# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：实现有上限的重试。
任务：修改 src/retry.py 的 run_with_retry(call, attempts=3)。
约束：最多调用 call() attempts 次。成功后必须立即停止。仅重试 ValueError；达到上限后重新抛出最后一个 ValueError。
验证：运行 python -m unittest discover -s tests。

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
