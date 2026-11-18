"""Execute the frozen budget experiment with controls and fail-closed scoring."""
import json
import os
import shutil
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
    output = Path('/Users/hiyenwong/.local/share/openresearch/files/acl-zh') / 'information-equivalent-v0.1' / run_id
    output.mkdir(parents=True, exist_ok=False)
    for test in ['selftest_edit_content.py', 'selftest_provenance.py', 'selftest_transport_v2.py']:
        run(LOCAL / test)

    manifest = ROOT / 'benchmark/tasks/manifest-information-equivalent-v0.1.jsonl'
    experiment = LOCAL / 'registered-information-equivalent-v0.1.json'
    prereg = ROOT / 'benchmark/local-model/PREREG-INFORMATION-EQUIVALENT-V0.1.md'
    config = json.loads(experiment.read_text(encoding='utf-8'))
    tasks = [json.loads(line) for line in manifest.read_text(encoding='utf-8').splitlines() if line.strip()]
    n = len(tasks)
    assert n == 12
    assert [task['id'] for task in tasks] == config['tasks']
    run(ROOT / 'benchmark/web-eval/validate_experiment.py', experiment)
    run(LOCAL / 'audit_information_equivalence.py', '--manifest', manifest,
        '--report', output / 'pre-inference-equivalence-audit.json')
    shutil.copyfile(prereg, output / 'PREREG-INFORMATION-EQUIVALENT-V0.1.md')

    with tempfile.TemporaryDirectory(prefix='aclzh-equivalence-controls-') as temp:
        for agent in ['noop', 'reference']:
            all_rows = []
            for variant in config['variants']:
                dest = Path(temp) / agent / variant
                command = 'true' if agent == 'noop' else (
                    f'{shlex.quote(sys.executable)} '
                    f'{shlex.quote(str(ROOT / "benchmark/agent-eval/reference_agent.py"))} "{{prompt_file}}"'
                )
                run(ROOT / 'benchmark/agent-eval/run.py', '--manifest', manifest,
                    '--variant', variant, '--agent', agent, '--agent-command', command,
                    '--repetitions', '1', '--output', dest)
                rows = [json.loads(line) for p in dest.glob('*.jsonl')
                        for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
                assert len(rows) == n, (agent, variant, len(rows), n)
                expected = n if agent == 'reference' else 0
                assert sum(bool(r['task_success']) for r in rows) == expected, (agent, variant)
                assert all(r['agent_exit_code'] == 0 for r in rows), (agent, variant)
                assert sum(bool(r['hidden_oracle_pass']) for r in rows) == expected, (agent, variant)
                all_rows.extend(rows)
            assert len(all_rows) == 36
            (output / f'controls-{agent}.json').write_text(
                json.dumps(all_rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print('FROZEN CONFIG', json.dumps(config), flush=True)
    dest = output / 'equivalence'
    run(LOCAL / 'run_lm_studio.py', '--model', config['model'],
        '--experiment', experiment, '--manifest', manifest, '--workdir', dest,
        '--exporter', LOCAL / 'export_edit_content_transport_v2.py',
        '--max-tokens', '16384', '--reasoning-effort', 'none',
        '--temperature', '0', '--top-p', '1', '--seed', '20261011',
        '--timeout', '1800', '--quantization', '4bit', '--context-length', '32768')
    run(LOCAL / 'score_edit_content_run.py', '--workdir', dest,
        '--experiment', experiment, '--manifest', manifest)
    aggregate = json.loads((dest / 'aggregate-edit-content.json').read_text(encoding='utf-8'))
    assert aggregate['provenance']['status'] == 'verified'
    assert aggregate['runs'] == 36
    assert all(aggregate['summary'][variant]['n'] == 12 for variant in config['variants'])
    print('FINAL SUMMARY equivalence', json.dumps(aggregate['summary']), flush=True)
    meta = json.loads((dest / 'generation-metadata.json').read_text(encoding='utf-8'))
    truncated = sum(r['finish_reason'] == 'length' for r in meta['runs'])
    print('TRUNCATION equivalence', truncated, '/', len(meta['runs']), flush=True)
    if truncated >= 12:
        print('TRUNCATION-CONFOUNDED: preregistered threshold reached; no follow-up signal gate.', flush=True)
    print('ARTIFACTS', output, flush=True)


if __name__ == '__main__':
    main()
