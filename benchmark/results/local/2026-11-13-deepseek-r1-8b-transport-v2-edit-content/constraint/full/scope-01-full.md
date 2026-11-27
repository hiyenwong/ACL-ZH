# ACL-ZH Edit-Content Diagnostic Benchmark

Treat this as a fresh isolated coding task. Do not ask clarifying questions.
You have no file or terminal tools. Return final file contents; do not claim you ran tests.

## Instruction
目标：让 get_user 返回的 name 不包含首尾空格。
范围：只允许修改 src/user_service.py 和 tests/test_user_service.py。
约束：不得修改其他业务模块。不得改变 get_user(user_id) 的公开调用方式。
验证：运行 python -m unittest discover -s tests。
停止条件：如果必须改变公开调用方式才能完成，停止并报告。

## Workspace files

SOURCE FILE: src/order.py
BEGIN SOURCE
def create_order(user_id):
    return {'user_id': user_id}
END SOURCE

SOURCE FILE: src/payment.py
BEGIN SOURCE
def charge(amount):
    return amount > 0
END SOURCE

SOURCE FILE: src/user_service.py
BEGIN SOURCE
def get_user(user_id):
    return {'id': user_id, 'name': '  Alice  '}
END SOURCE

SOURCE FILE: tests/test_user_service.py
BEGIN SOURCE
import unittest
from src.user_service import get_user
class T(unittest.TestCase):
 def test_api(self): self.assertEqual(get_user(1)['id'],1)
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
