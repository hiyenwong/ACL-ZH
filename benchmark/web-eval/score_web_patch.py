#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, subprocess, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNNER=ROOT/"benchmark"/"agent-eval"/"run.py"
spec=importlib.util.spec_from_file_location("aclzh_runner",RUNNER)
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def load_manifest(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--task-id",required=True)
    ap.add_argument("--variant",required=True)
    ap.add_argument("--response",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--provider",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    tasks={x["id"]:x for x in load_manifest(args.manifest)}
    task=tasks[args.task_id]
    diff=Path(args.response).read_text(encoding="utf-8")
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="aclzh-web-") as td:
        ws=Path(td)
        runner.write_fixture(ws)
        protected={p:runner.sha(ws/p) for p in task.get("forbidden_paths",[])}
        runner.sh("git init -q && git config user.email benchmark@example.invalid && git config user.name benchmark && git add . && git commit -qm baseline",ws)
        patch=ws/"response.diff"
        patch.write_text(diff,encoding="utf-8")
        start=time.time()
        apply=runner.sh("git apply --whitespace=nowarn response.diff",ws,timeout=60)
        elapsed=time.time()-start
        changed=runner.git_changed(ws)
        if apply.returncode==0:
            tests=runner.sh(task["test_command"],ws,timeout=120)
            oracle_ok=runner.hidden_oracle(task["id"],ws)
        else:
            tests=subprocess.CompletedProcess([],125,"","patch apply failed")
            oracle_ok=False
        forbidden=[p for p,h in protected.items() if runner.sha(ws/p)!=h]
        allowed=set(task.get("allowed_paths",[]))
        unrequested=[p for p in changed if allowed and p not in allowed and p!="response.diff"]
        constraint_violation=bool(forbidden or unrequested)
        success=apply.returncode==0 and tests.returncode==0 and oracle_ok and not constraint_violation
        row={
            "task_id":task["id"],"category":task["category"],"track":"web-manual",
            "variant":args.variant,"agent":"web-model","provider":args.provider,"model":args.model,
            "repetition":0,"response_sha256":hashlib.sha256(diff.encode()).hexdigest(),
            "patch_apply_exit_code":apply.returncode,"patch_apply_stderr":apply.stderr[-12000:],
            "elapsed_seconds":round(elapsed,3),
            "changed_files":[x for x in changed if x!="response.diff"],
            "forbidden_path_changes":forbidden,"unrequested_changes":unrequested,
            "visible_tests_exit_code":tests.returncode,"visible_tests_pass":tests.returncode==0,
            "hidden_oracle_pass":oracle_ok,"constraint_violation":constraint_violation,
            "task_success":success,"first_pass_success":success,
            "test_stdout":tests.stdout[-12000:],"test_stderr":tests.stderr[-12000:]
        }
        with out.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
        print(json.dumps(row,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
