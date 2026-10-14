# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
build_event 不要再打印东西了，只返回事件对象，结构别变。

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
