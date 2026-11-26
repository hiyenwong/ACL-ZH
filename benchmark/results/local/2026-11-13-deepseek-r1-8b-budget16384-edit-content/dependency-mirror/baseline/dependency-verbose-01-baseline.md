# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
现在这个 JSON 序列化结果虽然能被解析，但同一个对象在输出格式上不够稳定。我希望 key 按字母排序，同时尽量减少分隔符周围不必要的空格。这个改动只解决输出稳定性和紧凑性，不要为了它引入新的依赖。

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
