# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.

## Instruction
目标：让 normalize_options() 不修改调用方输入。
任务：返回 options 的新 dict，并把新 dict 中的 mode 转成小写。
约束：不得原地修改传入的 options。返回对象必须与输入对象不是同一个 dict。
验证：运行 python -m unittest discover -s tests。

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
