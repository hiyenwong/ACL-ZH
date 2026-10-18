# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
修改 normalize_options()：返回新的 dict；mode 转为小写；不得修改输入 options。

## Workspace files

### src/options.py
```python
def normalize_options(options):
    if 'mode' in options:
        options['mode'] = str(options['mode']).lower()
    return options
```

### tests/test_options.py
```python
import unittest
from src.options import normalize_options
class T(unittest.TestCase):
 def test_result(self): self.assertEqual(normalize_options({'mode':'FAST'})['mode'],'fast')
```

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.
