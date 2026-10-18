# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
token 去掉两边空格就行，函数签名和返回字符串这个行为别改。

## Workspace files

### src/token.py
```python
def normalize_token(token):
    return token
```

### tests/test_token.py
```python
import unittest
from src.token import normalize_token
class T(unittest.TestCase):
 def test_plain(self): self.assertEqual(normalize_token('abc'),'abc')
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
