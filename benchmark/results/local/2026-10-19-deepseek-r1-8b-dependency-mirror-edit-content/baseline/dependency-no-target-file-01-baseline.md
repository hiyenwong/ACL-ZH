# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
把 JSON 输出稳定一下，key 按字母排，输出紧凑一点，最好别为了这个加依赖。

## Workspace files

### requirements.txt
```python

```

### src/serializer.py
```python
import json

def dumps(value):
    return json.dumps(value)
```

### tests/test_serializer.py
```python
import json, unittest
from src.serializer import dumps
class T(unittest.TestCase):
 def test_valid_json(self): self.assertEqual(json.loads(dumps({'b':1,'a':2})),{'a':2,'b':1})
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
