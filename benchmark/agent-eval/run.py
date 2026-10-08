#!/usr/bin/env python3
import argparse, hashlib, json, os, random, shutil, subprocess, tempfile, time
from pathlib import Path

def load_manifest(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]

def write_fixture(root: Path):
    files = {
        "src/__init__.py": "",
        "src/user_service.py": "def get_user(user_id):\n    return {'id': user_id, 'name': 'alice'}\n",
        "src/payment.py": "def charge(amount):\n    return amount > 0\n",
        "src/order.py": "def create_order(user_id):\n    return {'user_id': user_id}\n",
        "src/config.py": "def parse_config(raw):\n    return dict(raw)\n\nclass ConfigLoader:\n    def load(self, raw):\n        return dict(raw)\n",
        "src/parser.py": "def parse_int(value):\n    return int(value)\n",
        "src/cache_service.py": "class CacheService:\n    def __init__(self, cache, query):\n        self.cache = cache\n        self.query = query\n    def get(self, key):\n        return self.query(key)\n",
        "src/names.py": "def normalize_name(value):\n    return value\n",
        "src/serializer.py": "import json\n\ndef dumps(value):\n    return json.dumps(value)\n",
        "schema.json": "{\"type\":\"object\"}\n",
        "requirements.txt": "",
        "tests/test_user_service.py": "import unittest\nfrom src.user_service import get_user\nclass T(unittest.TestCase):\n def test_api(self): self.assertEqual(get_user(1)['id'],1)\n",
        "tests/test_config.py": "import unittest\nfrom src.config import ConfigLoader, parse_config\nclass T(unittest.TestCase):\n def test_load(self): self.assertIsInstance(ConfigLoader().load({'a':1}),dict)\n",
        "tests/test_parser.py": "import unittest\nfrom src.parser import parse_int\nclass T(unittest.TestCase):\n def test_parse(self): self.assertEqual(parse_int('2'),2)\n",
        "tests/test_cache_service.py": "import unittest\nfrom src.cache_service import CacheService\nclass T(unittest.TestCase):\n def test_miss(self): self.assertEqual(CacheService({},lambda k:'db').get('x'),'db')\n",
        "tests/test_names.py": "import unittest\nfrom src.names import normalize_name\nclass T(unittest.TestCase):\n def test_name(self): self.assertEqual(normalize_name(' Alice '),' Alice ')\n",
        "tests/test_serializer.py": "import json, unittest\nfrom src.serializer import dumps\nclass T(unittest.TestCase):\n def test_json(self): self.assertEqual(json.loads(dumps({'b':1,'a':2})),{'a':2,'b':1})\n",
    }
    for path, content in files.items():
        p=root/path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

def sh(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True, check=check)

def git_changed(cwd):
    r=sh("git diff --name-only HEAD",cwd)
    return [x for x in r.stdout.splitlines() if x.strip()]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--variant",choices=["baseline","minimal","full"],required=True)
    ap.add_argument("--agent",required=True)
    ap.add_argument("--agent-command",required=True,help="Use {prompt_file} and/or {workspace}")
    ap.add_argument("--repetitions",type=int,default=1)
    ap.add_argument("--output",default="benchmark/results/agent")
    ap.add_argument("--seed",type=int,default=20261008)
    args=ap.parse_args()

    tasks=load_manifest(args.manifest)
    rng=random.Random(args.seed)
    runs=[(t,i) for t in tasks for i in range(args.repetitions)]
    rng.shuffle(runs)
    outdir=Path(args.output); outdir.mkdir(parents=True,exist_ok=True)
    outfile=outdir/f"{args.agent}-{args.variant}-{int(time.time())}.jsonl"

    with outfile.open("w",encoding="utf-8") as out:
        for task,rep in runs:
            with tempfile.TemporaryDirectory(prefix="aclzh-") as td:
                ws=Path(td)
                write_fixture(ws)
                sh("git init -q && git config user.email benchmark@example.invalid && git config user.name benchmark && git add . && git commit -qm baseline",ws)
                prompt=task[args.variant]
                prompt_file=ws/"PROMPT.txt"; prompt_file.write_text(prompt,encoding="utf-8")
                prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()
                cmd=args.agent_command.format(prompt_file=str(prompt_file),workspace=str(ws))
                start=time.time()
                proc=sh(cmd,ws)
                elapsed=time.time()-start
                changed=git_changed(ws)
                tests=sh(task["test_command"],ws)
                forbidden=[p for p in changed if p in task.get("forbidden_paths",[])]
                allowed=set(task.get("allowed_paths",[]))
                unrequested=[p for p in changed if allowed and p not in allowed and p!="PROMPT.txt"]
                row={
                    "task_id":task["id"],"category":task["category"],"variant":args.variant,
                    "agent":args.agent,"repetition":rep,"prompt_sha256":prompt_sha,
                    "agent_command":args.agent_command,"agent_exit_code":proc.returncode,
                    "elapsed_seconds":round(elapsed,3),"changed_files":changed,
                    "forbidden_path_changes":forbidden,"unrequested_changes":unrequested,
                    "tests_exit_code":tests.returncode,"tests_pass":tests.returncode==0,
                    "constraint_violation":bool(forbidden),
                    "task_success":tests.returncode==0 and not forbidden and not unrequested,
                    "stdout":proc.stdout[-12000:],"stderr":proc.stderr[-12000:],
                    "test_stdout":tests.stdout[-12000:],"test_stderr":tests.stderr[-12000:]
                }
                out.write(json.dumps(row,ensure_ascii=False)+"\n")
                out.flush()
    print(outfile)

if __name__=="__main__":
    main()
