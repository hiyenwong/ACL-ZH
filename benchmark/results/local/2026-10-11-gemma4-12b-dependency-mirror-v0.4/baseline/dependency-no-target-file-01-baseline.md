# ACL-ZH Web Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
把 JSON 输出稳定一下，key 按字母排，输出紧凑一点，最好别为了这个加依赖。

## Workspace files

### requirements.txt
```

```

### src/serializer.py
```
import json

def dumps(value):
    return json.dumps(value)
```

### tests/test_serializer.py
```
import json, unittest
from src.serializer import dumps
class T(unittest.TestCase):
 def test_valid_json(self): self.assertEqual(json.loads(dumps({'b':1,'a':2})),{'a':2,'b':1})
```

## Response contract

Return ONLY a unified diff that can be applied with git apply.
Do not include explanations, markdown fences, or prose.
Do not modify files outside the requested task.
