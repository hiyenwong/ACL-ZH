"""Execute the frozen budget experiment with controls and fail-closed scoring."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / 'benchmark/local-model'


def run(*args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)


def main():
    os.chdir(ROOT)
    run_id = os.environ['ORX_RUN_ID']
    output = Path('/Users/hiyenwong/.local/share/openresearch/files/acl-zh') / 'budget16384' / run_id
    output.mkdir(parents=True, exist_ok=False)
    for test in ['selftest_edit_content.py', 'selftest_provenance.py']:
        run(LOCAL / test)
    for family, version in [('dependency-mirror', 'v0.4'), ('constraint', 'v0.3')]:
        manifest = ROOT / f'benchmark/tasks/manifest-{family}-{version}.jsonl'
        experiment = LOCAL / f'registered-{family}.json'
        run(ROOT / 'benchmark/web-eval/validate_experiment.py', experiment)
        n = len(manifest.read_text().splitlines())
        with tempfile.TemporaryDirectory(prefix='aclzh-controls-') as temp:
            for agent in ['noop', 'reference']:
                dest = Path(temp) / agent
                command = 'true' if agent == 'noop' else (
                    f'{shlex.quote(sys.executable)} '
                    f'{shlex.quote(str(ROOT / "benchmark/agent-eval/reference_agent.py"))} "{{prompt_file}}"'
                )
                run(ROOT / 'benchmark/agent-eval/run.py', '--manifest', manifest,
                    '--variant', 'full', '--agent', agent, '--agent-command', command,
                    '--repetitions', '1', '--output', dest)
                rows = [json.loads(line) for p in dest.glob('*.jsonl')
                        for line in p.read_text().splitlines() if line.strip()]
                assert len(rows) == n, (family, agent, len(rows), n)
                assert sum(r['task_success'] for r in rows) == (n if agent == 'reference' else 0)
                if agent == 'noop':
                    assert not any(r['hidden_oracle_pass'] for r in rows)
                (output / f'controls-{family}-{agent}.json').write_text(json.dumps(rows, indent=2))
        config = json.loads(experiment.read_text())
        print('FROZEN CONFIG', json.dumps(config), flush=True)
        dest = output / family
        run(LOCAL / 'run_lm_studio.py', '--model', config['model'],
            '--experiment', experiment, '--manifest', manifest, '--workdir', dest,
            '--exporter', LOCAL / 'export_edit_content_prompts.py',
            '--max-tokens', '16384', '--reasoning-effort', 'none',
            '--temperature', '0', '--top-p', '1', '--seed', '20261011',
            '--timeout', '1800', '--quantization', '4bit')
        run(LOCAL / 'score_edit_content_run.py', '--workdir', dest,
            '--experiment', experiment, '--manifest', manifest)
        aggregate = json.loads((dest / 'aggregate-edit-content.json').read_text())
        assert aggregate['provenance']['status'] == 'verified'
        print('FINAL SUMMARY', family, json.dumps(aggregate['summary']), flush=True)
        meta = json.loads((dest / 'generation-metadata.json').read_text())
        truncated = sum(r['finish_reason'] == 'length' for r in meta['runs'])
        print('TRUNCATION', family, truncated, '/', len(meta['runs']), flush=True)
        if family == 'dependency-mirror' and truncated >= 6:
            print('STOP: preregistered truncation gate; constraint not launched.', flush=True)
            break
    print('ARTIFACTS', output, flush=True)


if __name__ == '__main__':
    main()
