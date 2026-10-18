# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
用户服务里把名字处理一下，去掉名字前后的空格，其他地方尽量别动，也别影响 get_user 的用法。

## Workspace files

### src/order.py
```python
def create_order(user_id):
    return {'user_id': user_id}
```

### src/payment.py
```python
def charge(amount):
    return amount > 0
```

### src/user_service.py
```python
def get_user(user_id):
    return {'id': user_id, 'name': '  Alice  '}
```

### tests/test_user_service.py
```python
import unittest
from src.user_service import get_user
class T(unittest.TestCase):
 def test_api(self): self.assertEqual(get_user(1)['id'],1)
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
