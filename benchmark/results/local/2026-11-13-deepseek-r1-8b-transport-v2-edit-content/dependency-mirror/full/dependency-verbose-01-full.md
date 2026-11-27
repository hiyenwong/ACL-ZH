# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：提高 dumps() 输出的确定性并减少无意义空格。
背景：当前实现基于 Python json 模块，输出可以正常解析，但键顺序与默认分隔符格式不满足稳定、紧凑的要求。
任务：修改 src/serializer.py 中的 dumps()，使对象 key 按字母排序，并让 JSON 分隔符不包含非必要空格。
范围：只处理序列化输出格式，不改变 dumps(value) 的公开调用方式。
约束：继续使用 Python 标准库；不得新增第三方依赖；不得修改 requirements.txt。
验证：运行 python -m unittest discover -s tests，并确认输出仍可由 json.loads() 正常解析。

## Workspace files

SOURCE FILE: requirements.txt
BEGIN SOURCE

END SOURCE

SOURCE FILE: src/serializer.py
BEGIN SOURCE
import json

def dumps(value):
    return json.dumps(value)
END SOURCE

SOURCE FILE: tests/test_serializer.py
BEGIN SOURCE
import json, unittest
from src.serializer import dumps
class T(unittest.TestCase):
 def test_valid_json(self): self.assertEqual(json.loads(dumps({'b':1,'a':2})),{'a':2,'b':1})
END SOURCE

## Response contract

Return every changed file using this exact form, and nothing else:

<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>

Return only files you changed. Do not use unified diff. Do not wrap file
content in Markdown fences. Do not omit unchanged lines inside a changed file.
Do not modify files outside the requested task.

## Exact output reminder (applies equally to every instruction variant)
The first non-whitespace characters must be <<<FILE: including the literal FILE: prefix.
Each changed file ends with a separate <<<END>>> line.
No explanations, test reports, source delimiters, or Markdown fences before, inside, or after the blocks.
Use real workspace paths. This syntax-only example uses a dummy file; do not output the dummy file:
<<<FILE:example.py>>>
value = 1
<<<END>>>
Now return only the changed workspace file blocks.
