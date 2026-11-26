"""Preregistered free-answer schema probe; no benchmark task content."""
import ast
import argparse
import json
import os
from pathlib import Path
import time
import urllib.error

from run_lm_studio import http_json


MODEL = 'deepseek/deepseek-r1-0528-qwen3-8b'
ARITHMETIC_TASKS = [
    {'id': 'arith-mixed-01', 'kind': 'arithmetic',
     'prompt': 'Compute ((17*23)-(312/6))%11.', 'expected': 9},
    {'id': 'arith-minmax-01', 'kind': 'arithmetic',
     'prompt': 'Compute max(38, -17, 46, 12) * min(9, 4, 17).', 'expected': 184},
    {'id': 'arith-sum-01', 'kind': 'arithmetic',
     'prompt': 'Compute sum([12, 15, 9, 31]) * 3.', 'expected': 201},
    {'id': 'arith-len-01', 'kind': 'arithmetic',
     'prompt': "Compute len('controlled-language') + 27.", 'expected': 46},
    {'id': 'arith-div-01', 'kind': 'arithmetic',
     'prompt': 'Compute (847 - 319) // 13.', 'expected': 40},
]
CODE_TASKS = [
    {'id': 'code-normalize-01', 'kind': 'code', 'prompt': 'Normalize the string value by removing surrounding whitespace and converting it to lowercase.', 'expression': 'value.strip().lower()',
     'cases': [{'input': {'value': '  ACL-ZH  '}, 'expected': 'acl-zh'}, {'input': {'value': 'Probe'}, 'expected': 'probe'}]},
    {'id': 'code-distance-01', 'kind': 'code', 'prompt': 'Return the absolute difference between the two numbers left and right.', 'expression': 'abs(left - right)',
     'cases': [{'input': {'left': 19, 'right': 47}, 'expected': 28}, {'input': {'left': -6, 'right': -13}, 'expected': 7}]},
    {'id': 'code-list-01', 'kind': 'code', 'prompt': 'For every string in the list items, remove surrounding whitespace and return the new list.', 'expression': '[item.strip() for item in items]',
     'cases': [{'input': {'items': [' a ', 'b']}, 'expected': ['a', 'b']}, {'input': {'items': ['  x']}, 'expected': ['x']}]},
    {'id': 'code-record-01', 'kind': 'code', 'prompt': "From user, return a new dict with only id and name; remove whitespace around name but do not change id.", 'expression': "{'id': user['id'], 'name': user['name'].strip()}",
     'cases': [{'input': {'user': {'id': 7, 'name': ' Ada '}}, 'expected': {'id': 7, 'name': 'Ada'}}, {'input': {'user': {'id': -2, 'name': 'LOVELACE'}}, 'expected': {'id': -2, 'name': 'LOVELACE'}}]},
    {'id': 'code-default-01', 'kind': 'code', 'prompt': "Return user.get('enabled', False), preserving False when present and using False when missing.", 'expression': "user.get('enabled', False)",
     'cases': [{'input': {'user': {'enabled': False}}, 'expected': False}, {'input': {'user': {}}, 'expected': False}]},
]
TASKS = ARITHMETIC_TASKS + CODE_TASKS
ORDER = [
    ('arith-mixed-01', False), ('arith-mixed-01', True),
    ('code-normalize-01', True), ('code-normalize-01', False),
    ('arith-minmax-01', False), ('arith-minmax-01', True),
    ('code-distance-01', True), ('code-distance-01', False),
    ('arith-sum-01', False), ('arith-sum-01', True),
    ('code-list-01', True), ('code-list-01', False),
    ('arith-len-01', False), ('arith-len-01', True),
    ('code-record-01', True), ('code-record-01', False),
    ('arith-div-01', False), ('arith-div-01', True),
    ('code-default-01', True), ('code-default-01', False),
]


def response_schema(task):
    properties = {'task_id': {'type': 'string', 'enum': [task['id']]}}
    if task['kind'] == 'arithmetic':
        properties['answer'] = {'type': 'integer'}
    else:
        properties['expression'] = {'type': 'string', 'minLength': 1}
    return {'type': 'object', 'properties': properties,
            'required': ['task_id'] + (['answer'] if task['kind'] == 'arithmetic' else ['expression']),
            'additionalProperties': False}


def instruction(task, constrained):
    field = 'answer (integer)' if task['kind'] == 'arithmetic' else 'expression (string)'
    wording = ('Return only one JSON object with exactly task_id and ' + field +
               '. The JSON must contain no extra fields. Do not explain.')
    if task['kind'] == 'code':
        var_names = ', '.join(sorted(task['cases'][0]['input'].keys()))
        wording += (f' Use the input variable(s): {var_names}.'
                    ' The expression must be a single Python expression, with no return keyword, assignment, import, statement, or code fence.')
    return {'role': 'user', 'content': task['prompt'] + '\n\n' + wording}


def schema_valid(content, task):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return False
    field = 'answer' if task['kind'] == 'arithmetic' else 'expression'
    return (isinstance(value, dict) and set(value) == {'task_id', field}
            and value['task_id'] == task['id']
            and (type(value[field]) is int if task['kind'] == 'arithmetic'
                 else isinstance(value[field], str) and bool(value[field])))


ALLOWED_NAMES = {'abs', 'False', 'None', 'True', 'float', 'int', 'len', 'max', 'min', 'sorted', 'str', 'sum'}
ALLOWED_METHODS = {'get', 'items', 'keys', 'lower', 'strip', 'upper', 'values'}
BUILTIN_VALUES = {'abs': abs, 'False': False, 'None': None, 'True': True,
                  'float': float, 'int': int, 'len': len, 'max': max,
                  'min': min, 'sorted': sorted, 'str': str, 'sum': sum}


def safe_eval(node, variables):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body, variables)
    if isinstance(node, ast.Constant) and type(node.value) in {bool, int, float, str, None.__class__}:
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.Name) and node.id in BUILTIN_VALUES:
        return BUILTIN_VALUES[node.id]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [safe_eval(item, variables) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {safe_eval(key, variables): safe_eval(value, variables)
                for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.Subscript):
        return safe_eval(node.value, variables)[safe_eval(node.slice, variables)]
    if isinstance(node, ast.Attribute) and node.attr in ALLOWED_METHODS:
        return getattr(safe_eval(node.value, variables), node.attr)
    if isinstance(node, ast.Call):
        function = safe_eval(node.func, variables)
        args = [safe_eval(arg, variables) for arg in node.args]
        kwargs = {keyword.arg: safe_eval(keyword.value, variables)
                  for keyword in node.keywords if keyword.arg}
        if function in {abs, float, int, len, max, min, sorted, str, sum}:
            return function(*args, **kwargs)
        return function(*args, **kwargs)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod)):
        left = safe_eval(node.left, variables)
        right = safe_eval(node.right, variables)
        if isinstance(node.op, ast.Add): return left + right
        if isinstance(node.op, ast.Sub): return left - right
        if isinstance(node.op, ast.Mult): return left * right
        if isinstance(node.op, ast.Div): return left / right
        if isinstance(node.op, ast.FloorDiv): return left // right
        return left % right
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
        value = safe_eval(node.operand, variables)
        if isinstance(node.op, ast.UAdd): return +value
        if isinstance(node.op, ast.USub): return -value
        return not value
    if isinstance(node, ast.BoolOp):
        values = [safe_eval(item, variables) for item in node.values]
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.Compare):
        left = safe_eval(node.left, variables)
        for operator, comparator in zip(node.ops, node.comparators):
            right = safe_eval(comparator, variables)
            if isinstance(operator, ast.Eq): passed = left == right
            elif isinstance(operator, ast.NotEq): passed = left != right
            elif isinstance(operator, ast.Lt): passed = left < right
            elif isinstance(operator, ast.LtE): passed = left <= right
            elif isinstance(operator, ast.Gt): passed = left > right
            elif isinstance(operator, ast.GtE): passed = left >= right
            else: raise ValueError('unsupported comparison')
            if not passed: return False
            left = right
        return True
    if isinstance(node, ast.IfExp):
        return safe_eval(node.body, variables) if safe_eval(node.test, variables) else safe_eval(node.orelse, variables)
    if isinstance(node, (ast.ListComp,)) and len(node.generators) == 1:
        generator = node.generators[0]
        if not isinstance(generator.target, ast.Name) or generator.ifs:
            raise ValueError('unsupported comprehension')
        source = safe_eval(generator.iter, variables)
        output = []
        for item in source:
            scoped = dict(variables)
            scoped[generator.target.id] = item
            output.append(safe_eval(node.elt, scoped))
        return output
    raise ValueError('unsupported expression node: ' + type(node).__name__)


def semantic_valid(content, task):
    try:
        value = json.loads(content)
        if task['kind'] == 'arithmetic':
            return type(value['answer']) is int and value['answer'] == task['expected']
        tree = ast.parse(value['expression'], mode='eval')
        return all(safe_eval(tree, dict(case['input'])) == case['expected'] for case in task['cases'])
    except Exception:
        return False


def self_test():
    assert len(TASKS) == len({task['id'] for task in TASKS}) == 10
    assert len(ORDER) == len(set(ORDER)) == 20
    assert {item[0] for item in ORDER} == {task['id'] for task in TASKS}
    for task in TASKS:
        schema_text = json.dumps(response_schema(task))
        if task['kind'] == 'arithmetic':
            assert str(task['expected']) not in schema_text
            assert semantic_valid(json.dumps({'task_id': task['id'], 'answer': task['expected']}), task)
        else:
            assert task['expression'] not in schema_text
            assert semantic_valid(json.dumps({'task_id': task['id'], 'expression': task['expression']}), task)
            expected_vars = set(task['cases'][0]['input'].keys())
            assert expected_vars, task['id']
            for case in task['cases']:
                assert set(case['input'].keys()) == expected_vars, task['id']
            for constrained_flag in (False, True):
                rendered = instruction(task, constrained_flag)['content']
                for var in expected_vars:
                    assert var in task['prompt'], (task['id'], var)
                    assert var in rendered, (task['id'], var, constrained_flag)
        assert not semantic_valid(json.dumps({'task_id': task['id'], 'answer': 999999}), task) if task['kind'] == 'arithmetic' else True
    assert not semantic_valid("{'task_id': 'x', 'expression': '__import__(\"os\").system(\"true\")'}", CODE_TASKS[0])
    print('free-answer schema task and safe evaluator self-test: PASS')


def main():
    self_test()
    base_dir = Path(os.environ.get('ACLZH_OUTPUT_ROOT', Path.home() / '.local/share/openresearch/files/acl-zh/schema-free-answer'))
    root = base_dir / os.environ['ORX_RUN_ID']
    root.mkdir(parents=True, exist_ok=False)
    config = {'model': MODEL, 'tasks': TASKS, 'order': ORDER,
              'max_tokens': 16384, 'temperature': 0, 'top_p': 1,
              'seed': 20261011, 'reasoning_effort': 'none',
              'source_commit': os.environ.get('ORX_COMMIT')}
    (root / 'configuration.json').write_text(json.dumps(config, indent=2))
    print('FROZEN CONFIG', json.dumps({'model': MODEL, 'tasks': len(TASKS), 'calls': len(ORDER), **{k: v for k, v in config.items() if k not in ('model', 'tasks', 'order')}}), flush=True)
    endpoint = 'http://127.0.0.1:1234/v1'
    available = http_json(endpoint + '/models', token=os.environ.get('LM_STUDIO_API_TOKEN'))
    (root / 'available-models.json').write_text(json.dumps(available, indent=2))
    assert MODEL in {item['id'] for item in available.get('data', [])}
    by_id = {task['id']: task for task in TASKS}
    rows = []
    for number, (task_id, constrained) in enumerate(ORDER, 1):
        task = by_id[task_id]
        payload = {'model': MODEL, 'messages': [instruction(task, constrained)],
                   'temperature': 0, 'top_p': 1, 'seed': 20261011,
                   'max_tokens': 16384, 'reasoning_effort': 'none', 'stream': False}
        if constrained:
            payload['response_format'] = {'type': 'json_schema', 'json_schema': {
                'name': 'aclzh_free_answer', 'strict': True,
                'schema': response_schema(task)}}
        (root / f'{number:02d}-request.json').write_text(json.dumps(payload, indent=2))
        started = time.time()
        result = http_json(endpoint + '/chat/completions', payload,
                           token=os.environ.get('LM_STUDIO_API_TOKEN'), timeout=1800)
        (root / f'{number:02d}-response.json').write_text(json.dumps(result, indent=2))
        content = result['choices'][0]['message'].get('content') or ''
        row = {'task_id': task_id, 'kind': task['kind'], 'constrained': constrained,
               'schema_valid': schema_valid(content, task),
               'semantic_valid': semantic_valid(content, task),
               'finish_reason': result['choices'][0].get('finish_reason'),
               'usage': result.get('usage'),
               'elapsed_seconds': time.time() - started}
        rows.append(row)
        (root / 'summary.json').write_text(json.dumps(rows, indent=2))
        print('PROBE', json.dumps(row), flush=True)
    print('FINAL SUMMARY', json.dumps(rows), flush=True)
    print('ARTIFACTS', root, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test-only', action='store_true')
    arguments = parser.parse_args()
    self_test()
    if not arguments.self_test_only:
        main()
