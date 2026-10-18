# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
修改 format_name()：先去掉 value 首尾空格，再按现有 uppercase 参数决定是否转大写。保持函数签名不变。

## Workspace files

### src/formatter.py
```python
def format_name(value, uppercase=False):
    return value.upper() if uppercase else value
```

### tests/test_formatter.py
```python
import unittest
from src.formatter import format_name
class T(unittest.TestCase):
 def test_upper(self): self.assertEqual(format_name('alice',True),'ALICE')
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
