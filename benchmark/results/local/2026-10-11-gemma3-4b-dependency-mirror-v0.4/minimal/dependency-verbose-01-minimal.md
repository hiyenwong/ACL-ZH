# ACL-ZH Web Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
修改 dumps() 的 JSON 输出格式：按 key 排序，并使用紧凑分隔符去掉非必要空格。保持现有调用方式。不要新增第三方依赖，也不要改 requirements.txt。

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
