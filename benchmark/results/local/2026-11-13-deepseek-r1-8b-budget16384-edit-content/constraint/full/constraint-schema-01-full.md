# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：压缩 payload。
任务：修改 src/payload.py 的 compact_payload()，返回不包含 None 值字段的新 dict。
约束：不得修改 schema.json。不得删除值为 0、False 或空字符串的字段。
验证：运行 python -m unittest discover -s tests。

## Workspace files

### schema.json
```python
{"type":"object"}
```

### src/payload.py
```python
def compact_payload(value):
    return dict(value)
```

### tests/test_payload.py
```python
import unittest
from src.payload import compact_payload
class T(unittest.TestCase):
 def test_copy(self): self.assertEqual(compact_payload({'a':1}),{'a':1})
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
