# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
修改 parse_id(value)：支持 ID-42 形式和普通数字字符串；返回值保持 int；保持单参数函数签名。

## Workspace files

### src/ids.py
```python
def parse_id(value):
    return int(value)
```

### tests/test_ids.py
```python
import unittest
from src.ids import parse_id
class T(unittest.TestCase):
 def test_int(self): self.assertEqual(parse_id('7'),7)
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
