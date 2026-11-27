# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
现在这个 JSON 序列化结果虽然能被解析，但同一个对象在输出格式上不够稳定。我希望 key 按字母排序，同时尽量减少分隔符周围不必要的空格。这个改动只解决输出稳定性和紧凑性，不要为了它引入新的依赖。

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
