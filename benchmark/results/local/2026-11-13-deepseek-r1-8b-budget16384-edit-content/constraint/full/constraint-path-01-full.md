# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：规范化邮箱地址。
任务：修改 src/profile.py 的 normalize_email()，去掉首尾空白并转换为小写。
范围：只允许修改 src/profile.py 和 tests/test_profile.py。
约束：不得修改 src/auth.py。
验证：运行 python -m unittest discover -s tests。

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
