# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
safe_divide 除零时别炸，返回空值就行，其他错误别乱吞。

## Workspace files

### src/safe_math.py
```python
def safe_divide(a, b):
    return a / b
```

### tests/test_safe_math.py
```python
import unittest
from src.safe_math import safe_divide
class T(unittest.TestCase):
 def test_normal(self): self.assertEqual(safe_divide(6,3),2)
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
