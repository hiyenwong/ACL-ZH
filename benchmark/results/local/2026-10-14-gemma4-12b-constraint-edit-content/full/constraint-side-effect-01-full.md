# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：移除 build_event() 的输出副作用。
任务：修改 src/audit.py，使 build_event(user_id, action) 只返回事件 dict。
约束：不得打印或写入 stdout/stderr。不得改变返回字段 user_id 和 action。
验证：运行 python -m unittest discover -s tests。

## Workspace files

### src/audit.py
```python
def build_event(user_id, action):
    print(action)
    return {'user_id': user_id, 'action': action}
```

### tests/test_audit.py
```python
import unittest
from src.audit import build_event
class T(unittest.TestCase):
 def test_shape(self): self.assertEqual(build_event(1,'login')['user_id'],1)
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
