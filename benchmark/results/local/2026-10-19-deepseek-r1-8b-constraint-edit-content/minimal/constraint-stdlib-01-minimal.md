# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
实现 sha256_text()：返回输入字符串的 SHA-256 十六进制摘要。只使用 Python 标准库，不要新增依赖。

## Workspace files

### requirements.txt
```python

```

### src/hashutil.py
```python
def sha256_text(value):
    return value
```

### tests/test_hashutil.py
```python
import unittest
from src.hashutil import sha256_text
class T(unittest.TestCase):
 def test_callable(self): self.assertTrue(callable(sha256_text))
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
