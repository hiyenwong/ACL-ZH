# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：规范 token 空白。
任务：修改 src/token.py 的 normalize_token(token)，去掉首尾空白。
约束：不得修改公开函数签名。返回类型必须保持 str。不得增加额外编码或大小写转换。
验证：运行 python -m unittest discover -s tests。

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
