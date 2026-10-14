#!/usr/bin/env python3
"""Export prompt bundles for the edit-content diagnostic track.

Same bundle layout and CLI as web-eval/export_web_prompts.py so that
run_lm_studio.py can use it via --exporter. Only the response contract
differs: complete file contents in <<<FILE:...>>> blocks instead of a
unified diff.

The contract text is frozen together with edit_content_parser.py.
"""
import argparse, importlib.util, json, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "agent-eval" / "run.py"
spec = importlib.util.spec_from_file_location("aclzh_runner", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

CONTRACT = [
    '## Response contract',
    '',
    'Return every changed file using this exact form, and nothing else:',
    '',
    '<<<FILE:path/to/file>>>',
    '<complete final file content>',
    '<<<END>>>',
    '',
    'Return only files you changed. Do not use unified diff. Do not wrap file',
    'content in Markdown fences. Do not omit unchanged lines inside a changed file.',
    'Do not modify files outside the requested task.',
]


def load_manifest(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--variant", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    tasks = load_manifest(args.manifest)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        runner.write_fixture(ws)
        source_files = {}
        for p in sorted(ws.rglob("*")):
            if p.is_file():
                rel = p.relative_to(ws).as_posix()
                source_files[rel] = p.read_text(encoding="utf-8")

    index = []
    for task in tasks:
        if args.variant not in task:
            raise SystemExit(f"{args.variant} missing from {task['id']}")
        relevant = sorted(set(task.get("allowed_paths", [])) | set(task.get("forbidden_paths", [])))
        files = {p: source_files[p] for p in relevant if p in source_files}
        payload = {
            "task_id": task["id"], "category": task["category"],
            "track": "local-edit-content",
            "variant": args.variant, "instruction": task[args.variant], "files": files,
            "allowed_paths": task.get("allowed_paths", []),
            "forbidden_paths": task.get("forbidden_paths", []),
            "test_command": task["test_command"],
        }
        json_path = out / f"{task['id']}-{args.variant}.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        chunks = ['# ACL-ZH Edit-Content Diagnostic Benchmark', '',
                  'Treat this as a fresh isolated coding task. Do not ask clarifying questions.', '',
                  '## Instruction', task[args.variant], '', '## Workspace files']
        for path, content in files.items():
            chunks += ['', f'### {path}', '```python', content.rstrip(), '```']
        chunks += [''] + CONTRACT + ['']
        md_path = out / f"{task['id']}-{args.variant}.md"
        md_path.write_text("\n".join(chunks), encoding="utf-8")
        index.append({"task_id": task["id"], "variant": args.variant,
                      "prompt": str(md_path), "metadata": str(json_path)})
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"tasks": len(index), "variant": args.variant, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
