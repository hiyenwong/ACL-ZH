"""Preregistered local schema capability probe; no benchmark scores."""
import json
import os
from pathlib import Path
import time
import urllib.error

from run_lm_studio import http_json

MODEL = 'deepseek/deepseek-r1-0528-qwen3-8b'
SCHEMA = {'type': 'object', 'properties': {
    'status': {'type': 'string', 'enum': ['ACLZH_PROBE_OK']},
    'count': {'type': 'integer', 'enum': [7]}},
    'required': ['status', 'count'], 'additionalProperties': False}
CASES = [
    ('cooperative', 'Return only a JSON object with status ACLZH_PROBE_OK and integer count 7.'),
    ('plain_text', 'Return only the plain text WRONG. Do not output JSON or an object.'),
    ('wrong_type', 'Return JSON with status WRONG, count as the string seven, and an extra field debug set to true.')]
ORDER = [(0, False), (0, True), (1, True), (1, False), (2, False), (2, True)]


def valid(content):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return False
    return (isinstance(value, dict) and set(value) == {'status', 'count'}
            and value['status'] == 'ACLZH_PROBE_OK'
            and type(value['count']) is int and value['count'] == 7)


def main():
    root = Path('/Users/hiyenwong/.local/share/openresearch/files/acl-zh/schema-capability') / os.environ['ORX_RUN_ID']
    root.mkdir(parents=True, exist_ok=False)
    config = {'model': MODEL, 'schema': SCHEMA, 'cases': CASES, 'order': ORDER,
              'max_tokens': 16384, 'temperature': 0, 'top_p': 1,
              'seed': 20261011, 'reasoning_effort': 'none',
              'source_commit': os.environ.get('ORX_COMMIT')}
    (root / 'configuration.json').write_text(json.dumps(config, indent=2))
    print('FROZEN CONFIG', json.dumps(config), flush=True)
    endpoint = 'http://127.0.0.1:1234/v1'
    models = http_json(endpoint + '/models', token=os.environ.get('LM_STUDIO_API_TOKEN'))
    (root / 'available-models.json').write_text(json.dumps(models, indent=2))
    rows = []
    for i, (case, constrained) in enumerate(ORDER, 1):
        name, prompt = CASES[case]
        payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}],
                   'temperature': 0, 'top_p': 1, 'seed': 20261011,
                   'max_tokens': 16384, 'reasoning_effort': 'none', 'stream': False}
        if constrained:
            payload['response_format'] = {'type': 'json_schema', 'json_schema': {
                'name': 'aclzh_probe', 'strict': True, 'schema': SCHEMA}}
        (root / f'{i:02d}-request.json').write_text(json.dumps(payload, indent=2))
        start = time.time()
        try:
            result = http_json(endpoint + '/chat/completions', payload,
                               token=os.environ.get('LM_STUDIO_API_TOKEN'), timeout=1800)
        except urllib.error.HTTPError as exc:
            error = exc.read().decode('utf-8', errors='replace')
            row = {'case': name, 'constrained': constrained, 'http_status': exc.code,
                   'error': error, 'elapsed_seconds': time.time() - start}
            (root / f'{i:02d}-error.json').write_text(json.dumps(row, indent=2))
            rows.append(row)
            (root / 'summary.json').write_text(json.dumps(rows, indent=2))
            print('PROBE', json.dumps(row), flush=True)
            if exc.code == 400 and ('schema' in error.lower() or 'response_format' in error.lower()):
                continue  # API rejection is a probe outcome, never retried.
            raise
        (root / f'{i:02d}-response.json').write_text(json.dumps(result, indent=2))
        choice = result['choices'][0]
        row = {'case': name, 'constrained': constrained, 'http_status': 200,
               'schema_valid': valid(choice['message'].get('content')),
               'finish_reason': choice.get('finish_reason'), 'usage': result.get('usage'),
               'elapsed_seconds': time.time() - start}
        rows.append(row)
        (root / 'summary.json').write_text(json.dumps(rows, indent=2))
        print('PROBE', json.dumps(row), flush=True)
    print('FINAL SUMMARY', json.dumps(rows), flush=True)
    print('ARTIFACTS', root, flush=True)


if __name__ == '__main__':
    main()
