# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：让 get_user 返回的 name 不包含首尾空格。
范围：只允许修改 src/user_service.py 和 tests/test_user_service.py。
约束：不得修改其他业务模块。不得改变 get_user(user_id) 的公开调用方式。
验证：运行 python -m unittest discover -s tests。
停止条件：如果必须改变公开调用方式才能完成，停止并报告。

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
