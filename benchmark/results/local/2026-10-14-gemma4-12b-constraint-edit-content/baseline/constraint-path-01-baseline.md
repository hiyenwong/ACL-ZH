# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
profile 里的邮箱整理一下，去掉两边空格并转小写，认证模块别碰。

## Workspace files

### src/auth.py
```python
AUTH_VERSION = 1
```

### src/profile.py
```python
def normalize_email(value):
    return value
```

### tests/test_profile.py
```python
import unittest
from src.profile import normalize_email
class T(unittest.TestCase):
 def test_plain(self): self.assertEqual(normalize_email('a@b.com'),'a@b.com')
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
