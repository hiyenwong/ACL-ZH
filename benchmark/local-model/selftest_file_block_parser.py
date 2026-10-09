#!/usr/bin/env python3
import importlib.util
from pathlib import Path

p=Path(__file__).with_name('file_block_parser.py')
spec=importlib.util.spec_from_file_location('file_block_parser',p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

one='''<<<src/a.py>>>\n```python\nprint("a")\n```'''
assert m.extract_blocks(one)==[('src/a.py','print("a")\n')]

two='''<<<src/a.py>>>\n```python\na=1\n```\n\n<<<tests/test_a.py>>>\n```python\nassert True\n```'''
assert m.extract_blocks(two)==[('src/a.py','a=1\n'),('tests/test_a.py','assert True\n')]

bad='''Here is the code:\n```python\na=1\n```'''
assert m.extract_blocks(bad)==[]

wrong='''<<<FILE:src/a.py>>>\nnot a fence'''
assert m.extract_blocks(wrong)==[]

print('file-block parser self-test: PASS')
