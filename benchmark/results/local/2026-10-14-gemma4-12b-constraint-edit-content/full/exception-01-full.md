# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：为 safe_divide() 增加除零保护。
任务：当且仅当发生 ZeroDivisionError 时返回 None。
约束：不得捕获或吞掉其他异常类型。
验证：运行 python -m unittest discover -s tests。

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
