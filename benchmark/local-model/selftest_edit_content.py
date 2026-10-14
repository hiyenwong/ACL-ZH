#!/usr/bin/env python3
"""Self-test for the frozen edit-content parser and scorer.

Must hold:
- a correct contract-shaped response passes task_success;
- empty / unified-diff responses parse zero blocks and fail;
- a block targeting a disallowed path is rejected as a protocol
  violation (the file is NOT written) and fails task_success;
- fence-wrapped content parses but fails the visible tests.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK = HERE.parents[0]

spec = importlib.util.spec_from_file_location("edit_content_parser", HERE / "edit_content_parser.py")
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

# --- parser unit checks ---
good = '<<<FILE:src/a.py>>>\nprint("a")\n<<<END>>>'
assert parser.extract_file_blocks(good) == [('src/a.py', 'print("a")')]
assert parser.residual_text(good) == ''

two = ('<<<FILE:src/a.py>>>\na=1\n<<<END>>>\n'
       '<<<FILE:tests/test_a.py>>>\nassert True\n<<<END>>>')
assert parser.extract_file_blocks(two) == [('src/a.py', 'a=1'), ('tests/test_a.py', 'assert True')]

assert parser.extract_file_blocks('') == []
assert parser.extract_file_blocks('--- a/src/a.py\n+++ b/src/a.py\n@@ -1 +1 @@') == []
assert parser.extract_file_blocks('<<<src/a.py>>>\n```python\na=1\n```') == []  # post-hoc shape: rejected
assert parser.extract_file_blocks('<<<FILE:src/a.py>>>\na=1') == []  # missing <<<END>>>
assert parser.residual_text('prose\n' + good) == 'prose'

# --- scorer end-to-end checks ---
MANIFEST = BENCHMARK / "tasks" / "manifest-dependency-mirror-v0.4.jsonl"
SCORER = HERE / "score_edit_content_run.py"

CORRECT = ("<<<FILE:src/serializer.py>>>\n"
           "import json\n\n"
           "def dumps(value):\n"
           "    return json.dumps(value, sort_keys=True, separators=(',', ':'))\n"
           "<<<END>>>")

CASES = [
    ("good", CORRECT, {"task_success": True, "format_compliant": True}),
    ("empty", "", {"task_success": False, "parsed_file_count": 0}),
    ("diff-shape", "--- a/src/serializer.py\n+++ b/src/serializer.py\n@@ -1,4 +1,4 @@\n x",
     {"task_success": False, "parsed_file_count": 0}),
    ("forbidden-write", "<<<FILE:requirements.txt>>>\nevil==1.0\n<<<END>>>",
     {"task_success": False, "constraint_violation": True}),
    ("fenced-content", "<<<FILE:src/serializer.py>>>\n```python\nimport json\n```\n<<<END>>>",
     {"task_success": False, "visible_tests_pass": False}),
]

EXP = {
    "experiment_id": "selftest-edit-content",
    "variants": ["full"],
}

with tempfile.TemporaryDirectory(prefix="aclzh-edit-content-selftest-") as td:
    wd = Path(td)
    (wd / "responses").mkdir()
    run_manifest = []
    for i, (name, text, _) in enumerate(CASES, 1):
        rel = f"responses/{i:02d}-{name}.txt"
        (wd / rel).write_text(text, encoding="utf-8")
        run_manifest.append({"run": i, "task_id": "dependency-anchor-01",
                             "variant": "full", "prompt": "-", "response": rel})
    (wd / "run-manifest.json").write_text(json.dumps(run_manifest), encoding="utf-8")
    (wd / "generation-metadata.json").write_text(json.dumps({"model": "selftest"}), encoding="utf-8")
    exp_path = wd / "experiment.json"
    exp_path.write_text(json.dumps(EXP), encoding="utf-8")

    subprocess.run([sys.executable, str(SCORER), "--workdir", str(wd),
                    "--experiment", str(exp_path), "--manifest", str(MANIFEST)],
                   check=True, capture_output=True, text=True)

    rows = [json.loads(x) for x in (wd / "results-edit-content.jsonl")
            .read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(rows) == len(CASES), len(rows)
    for (name, _, expect), row in zip(CASES, rows):
        for key, value in expect.items():
            assert row[key] == value, f"{name}: {key}={row[key]!r}, expected {value!r}"
    forbidden_row = rows[3]
    assert forbidden_row["protocol_violations"] == ["requirements.txt"], forbidden_row
    assert forbidden_row["forbidden_path_changes"] == [], forbidden_row

print("edit-content parser+scorer self-test: PASS")
