"""Check wrapper-only intervention preserves instructions and fixture bytes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[1]


def main():
    spec = importlib.util.spec_from_file_location('transport', LOCAL / 'export_edit_content_transport_v2.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parser_spec = importlib.util.spec_from_file_location('parser', LOCAL / 'edit_content_parser.py')
    parser = importlib.util.module_from_spec(parser_spec)
    parser_spec.loader.exec_module(parser)
    assert parser.extract_file_blocks('<<<FILE:example.py>>>\nvalue = 1\n<<<END>>>') == [('example.py', 'value = 1')]
    with tempfile.TemporaryDirectory() as td:
        for family, version in [('dependency-mirror', 'v0.4'), ('constraint', 'v0.3')]:
            manifest = ROOT / f'benchmark/tasks/manifest-{family}-{version}.jsonl'
            for variant in ['baseline', 'minimal', 'full']:
                outputs = []
                for exporter in ['export_edit_content_prompts.py', 'export_edit_content_transport_v2.py']:
                    out = Path(td) / family / variant / exporter
                    subprocess.run([sys.executable, str(LOCAL / exporter), '--manifest', str(manifest),
                                    '--variant', variant, '--output', str(out)], check=True, capture_output=True)
                    outputs.append(out)
                for old in outputs[0].glob('*.json'):
                    if old.name == 'index.json':
                        continue
                    before = json.loads(old.read_text())
                    after = json.loads((outputs[1] / old.name).read_text())
                    assert before == after, old.name
                    prompt = (outputs[1] / old.with_suffix('.md').name).read_text()
                    assert before['instruction'] in prompt
                    for content in before['files'].values():
                        assert content.rstrip() in prompt
                    assert '```' not in prompt
                    assert 'literal FILE: prefix' in prompt
    print('transport v2 fixture/instruction preservation: PASS')


if __name__ == '__main__':
    main()
