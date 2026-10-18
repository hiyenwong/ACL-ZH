# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
payload 输出时把值是 None 的字段去掉，但 schema 别动。

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
