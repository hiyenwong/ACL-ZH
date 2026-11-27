# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：增强 parse_id() 的输入兼容性。
任务：允许 value 是 ID-42 形式或普通数字字符串，并正确解析为整数。
约束：parse_id(value) 的公开签名不得改变。返回类型必须保持 int。不得改变普通数字字符串的既有行为。
验证：运行 python -m unittest discover -s tests。

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
