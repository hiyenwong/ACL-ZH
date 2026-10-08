#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import random
import subprocess
import tempfile
import time
from pathlib import Path


def load_manifest(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def write_fixture(root: Path):
    files = {
        "src/__init__.py": "",
        "src/user_service.py": "def get_user(user_id):\n    return {'id': user_id, 'name': '  Alice  '}\n",
        "src/payment.py": "def charge(amount):\n    return amount > 0\n",
        "src/order.py": "def create_order(user_id):\n    return {'user_id': user_id}\n",
        "src/config.py": "def parse_config(raw):\n    return dict(raw)\n\nclass ConfigLoader:\n    def load(self, raw):\n        return dict(raw)\n",
        "src/parser.py": "def parse_bool(value):\n    return bool(value)\n",
        "src/cache_service.py": "class CacheService:\n    def __init__(self, cache, query):\n        self.cache = cache\n        self.query = query\n    def get(self, key):\n        return self.query(key)\n",
        "src/names.py": "def normalize_name(value):\n    return value\n",
        "src/serializer.py": "import json\n\ndef dumps(value):\n    return json.dumps(value)\n",
        "schema.json": "{\"type\":\"object\"}\n",
        "requirements.txt": "",
        "tests/test_user_service.py": "import unittest\nfrom src.user_service import get_user\nclass T(unittest.TestCase):\n def test_api(self): self.assertEqual(get_user(1)['id'],1)\n",
        "tests/test_config.py": "import unittest\nfrom src.config import ConfigLoader\nclass T(unittest.TestCase):\n def test_load_type(self): self.assertIsInstance(ConfigLoader().load({'a':1}),dict)\n",
        "tests/test_parser.py": "import unittest\nfrom src.parser import parse_bool\nclass T(unittest.TestCase):\n def test_python_bool(self): self.assertTrue(parse_bool(True))\n",
        "tests/test_cache_service.py": "import unittest\nfrom src.cache_service import CacheService\nclass T(unittest.TestCase):\n def test_miss(self): self.assertEqual(CacheService({},lambda k:'db').get('x'),'db')\n",
        "tests/test_names.py": "import unittest\nfrom src.names import normalize_name\nclass T(unittest.TestCase):\n def test_plain(self): self.assertEqual(normalize_name('Alice'),'Alice')\n",
        "tests/test_serializer.py": "import json, unittest\nfrom src.serializer import dumps\nclass T(unittest.TestCase):\n def test_valid_json(self): self.assertEqual(json.loads(dumps({'b':1,'a':2})),{'a':2,'b':1})\n",
    }
    for path, content in files.items():
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def sh(cmd, cwd, timeout=None):
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=e.stdout or "",
            stderr=(e.stderr or "") + "\nTIMEOUT",
        )


def sha(path):
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def load_module(workspace, name, rel):
    path = workspace / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hidden_oracle(task_id, workspace):
    try:
        if task_id == "scope-01":
            import inspect
            m = load_module(workspace, "u", "src/user_service.py")
            value = m.get_user(7)
            return value == {"id": 7, "name": "Alice"} and list(inspect.signature(m.get_user).parameters) == ["user_id"]
        if task_id == "reference-01":
            m = load_module(workspace, "c", "src/config.py")
            a = m.ConfigLoader().load({"debug": "true"})
            b = m.ConfigLoader().load({"debug": "false"})
            return isinstance(a, dict) and a["debug"] is True and b["debug"] is False
        if task_id == "multi-action-01":
            m = load_module(workspace, "p", "src/parser.py")
            return m.parse_bool("false") is False and m.parse_bool("true") is True
        if task_id == "flow-01":
            m = load_module(workspace, "cs", "src/cache_service.py")
            calls = []
            svc = m.CacheService({"x": "cached"}, lambda k: (calls.append(k) or "db"))
            hit = svc.get("x")
            miss = svc.get("y")
            return hit == "cached" and miss == "db" and calls == ["y"]
        if task_id == "validation-01":
            m = load_module(workspace, "n", "src/names.py")
            return m.normalize_name("  Alice   Bob \t Smith  ") == "Alice Bob Smith"
        if task_id == "dependency-01":
            m = load_module(workspace, "s", "src/serializer.py")
            return m.dumps({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    except Exception:
        return False
    return False


def git_changed(cwd):
    tracked = sh("git diff --name-only HEAD", cwd).stdout.splitlines()
    untracked = sh("git ls-files --others --exclude-standard", cwd).stdout.splitlines()
    return sorted(set(x.strip() for x in tracked + untracked if x.strip()))


def read_cli_version(command):
    if not command:
        return None
    p = sh(command, Path.cwd(), timeout=30)
    value = (p.stdout or p.stderr).strip()
    return value[:1000] if value else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--variant", required=True, help="Prompt field name in each manifest row")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--agent-command", required=True, help="Command template. Placeholders: {prompt_file}, {workspace}")
    ap.add_argument("--repetitions", type=int, default=1)
    ap.add_argument("--output", default="benchmark/results/agent")
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--model", default=None)
    ap.add_argument("--reasoning-effort", default=None)
    ap.add_argument("--cli-version-command", default=None)
    ap.add_argument("--run-label", default=None)
    args = ap.parse_args()

    tasks = load_manifest(args.manifest)
    missing = [t.get("id", "<unknown>") for t in tasks if args.variant not in t]
    if missing:
        raise SystemExit(f"variant {args.variant!r} missing from tasks: {missing}")
    rng = random.Random(args.seed)
    runs = [(t, i) for t in tasks for i in range(args.repetitions)]
    rng.shuffle(runs)

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    traces = outdir / "traces"
    traces.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    outfile = outdir / f"{args.agent}-{args.variant}-{stamp}.jsonl"
    cli_version = read_cli_version(args.cli_version_command)

    with outfile.open("w", encoding="utf-8") as out:
        for task, rep in runs:
            with tempfile.TemporaryDirectory(prefix="aclzh-workspace-") as td, tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix="aclzh-prompt-", suffix=".txt", delete=True
            ) as pf:
                ws = Path(td)
                write_fixture(ws)
                protected = {p: sha(ws / p) for p in task.get("forbidden_paths", [])}
                sh(
                    "git init -q && git config user.email benchmark@example.invalid && "
                    "git config user.name benchmark && git add . && git commit -qm baseline",
                    ws,
                )

                prompt = task[args.variant]
                pf.write(prompt)
                pf.flush()
                prompt_sha = hashlib.sha256(prompt.encode()).hexdigest()
                cmd = args.agent_command.format(prompt_file=pf.name, workspace=str(ws))

                start = time.time()
                proc = sh(cmd, ws, timeout=args.timeout_seconds)
                elapsed = time.time() - start

                trace_base = f"{task['id']}-{args.variant}-r{rep}"
                stdout_path = traces / f"{trace_base}.stdout.log"
                stderr_path = traces / f"{trace_base}.stderr.log"
                stdout_path.write_text(proc.stdout or "", encoding="utf-8")
                stderr_path.write_text(proc.stderr or "", encoding="utf-8")

                changed = git_changed(ws)
                tests = sh(task["test_command"], ws, timeout=120)
                oracle_ok = hidden_oracle(task["id"], ws)
                forbidden = [p for p, h in protected.items() if sha(ws / p) != h]
                allowed = set(task.get("allowed_paths", []))
                unrequested = [p for p in changed if allowed and p not in allowed]
                constraint_violation = bool(forbidden or unrequested)
                success = tests.returncode == 0 and oracle_ok and not constraint_violation

                row = {
                    "task_id": task["id"],
                    "category": task["category"],
                    "track": task.get("track", "controlled"),
                    "variant": args.variant,
                    "agent": args.agent,
                    "model": args.model,
                    "reasoning_effort": args.reasoning_effort,
                    "cli_version": cli_version,
                    "run_label": args.run_label,
                    "repetition": rep,
                    "prompt_sha256": prompt_sha,
                    "agent_command_template": args.agent_command,
                    "agent_exit_code": proc.returncode,
                    "elapsed_seconds": round(elapsed, 3),
                    "changed_files": changed,
                    "forbidden_path_changes": forbidden,
                    "unrequested_changes": unrequested,
                    "visible_tests_exit_code": tests.returncode,
                    "visible_tests_pass": tests.returncode == 0,
                    "hidden_oracle_pass": oracle_ok,
                    "constraint_violation": constraint_violation,
                    "task_success": success,
                    "first_pass_success": success,
                    "stdout_trace": str(stdout_path),
                    "stderr_trace": str(stderr_path),
                    "test_stdout": tests.stdout[-12000:],
                    "test_stderr": tests.stderr[-12000:],
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()

    print(outfile)


if __name__ == "__main__":
    main()
