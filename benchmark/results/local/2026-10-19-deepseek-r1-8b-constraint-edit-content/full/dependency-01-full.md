# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：让 dumps() 输出稳定、紧凑的 JSON。
任务：修改 src/serializer.py，使 key 按字母排序，并移除非必要空格。
约束：不得新增第三方依赖。不得修改 requirements.txt。
验证：运行 python -m unittest discover -s tests。

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
