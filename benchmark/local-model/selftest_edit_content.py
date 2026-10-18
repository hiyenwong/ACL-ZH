#!/usr/bin/env python3
"""Self-test for the frozen edit-content parser and scorer.

Must hold:
- a correct contract-shaped response passes task_success;
- empty / unified-diff responses parse zero blocks and fail;
- a block targeting a disallowed path is rejected as a protocol
  violation (the file is NOT written) and fails task_success;
- fence-wrapped block content is a format violation and fails both
  visible tests (fences land in the written file) and task_success;
- residual prose around a correct block is semantic_task_success but
  NOT format_compliant, hence NOT task_success;
- a duplicate file path across blocks is a format violation, so a
  semantically correct response still fails task_success.
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

CORRECT_BODY = ("import json\n\n"
                "def dumps(value):\n"
                "    return json.dumps(value, sort_keys=True, separators=(',', ':'))")

CASES = [
    # Legal response: contract-shaped, semantically correct.
    ("good", CORRECT,
     {"task_success": True, "semantic_task_success": True, "format_compliant": True}),
    # No parseable blocks at all.
    ("empty", "",
     {"task_success": False, "semantic_task_success": False,
      "format_compliant": False, "parsed_file_count": 0}),
    ("diff-shape", "--- a/src/serializer.py\n+++ b/src/serializer.py\n@@ -1,4 +1,4 @@\n x",
     {"task_success": False, "format_compliant": False, "parsed_file_count": 0}),
    # Forbidden path: rejected as protocol violation, file not written.
    ("forbidden-write", "<<<FILE:requirements.txt>>>\nevil==1.0\n<<<END>>>",
     {"task_success": False, "semantic_task_success": False,
      "constraint_violation": True, "format_compliant": False}),
    # Fence-wrapped content (```): format violation AND the fences land
    # in the written file, so visible tests fail too (the gemma-3-4b
    # shape).
    ("fenced-content",
     "<<<FILE:src/serializer.py>>>\n```python\n" + CORRECT_BODY + "\n```\n<<<END>>>",
     {"task_success": False, "semantic_task_success": False,
      "visible_tests_pass": False, "format_compliant": False}),
    # Tilde fences (~~~) are equally forbidden; checking only ``` would
    # miss this shape.
    ("tilde-fenced-content",
     "<<<FILE:src/serializer.py>>>\n~~~python\n" + CORRECT_BODY + "\n~~~\n<<<END>>>",
     {"task_success": False, "semantic_task_success": False,
      "visible_tests_pass": False, "format_compliant": False}),
    # A fence line anywhere in the content is a violation, not only a
    # wrapped block. (Also breaks the written Python, so tests fail.)
    ("interior-fence",
     "<<<FILE:src/serializer.py>>>\nimport json\n```\n" + CORRECT_BODY + "\n<<<END>>>",
     {"task_success": False, "semantic_task_success": False,
      "visible_tests_pass": False, "format_compliant": False}),
    # Residual prose around a correct block: semantically successful but
    # a contract failure, so task_success must be False.
    ("residual-prose", "Here is the corrected file:\n" + CORRECT,
     {"semantic_task_success": True, "format_compliant": False, "task_success": False}),
    # Duplicate file path: contract violation even when the content is
    # semantically correct (last write wins, tests and oracle pass).
    ("duplicate-path", CORRECT + "\n" + CORRECT,
     {"semantic_task_success": True, "format_compliant": False,
      "task_success": False, "parsed_file_count": 2}),
]

FORMAT_VIOLATION_MARKERS = {
    "fenced-content": "markdown_fence_in_content:src/serializer.py",
    "tilde-fenced-content": "markdown_fence_in_content:src/serializer.py",
    "interior-fence": "markdown_fence_in_content:src/serializer.py",
    "residual-prose": "residual_text",
    "duplicate-path": "duplicate_file_path:src/serializer.py",
}

EXP = {
    "experiment_id": "selftest-edit-content",
    "variants": ["full"],
}

with tempfile.TemporaryDirectory(prefix="aclzh-edit-content-selftest-") as td:
    wd = Path(td)
    (wd / "responses").mkdir()
    (wd / "full").mkdir()
    run_manifest = []
    for i, (name, text, _) in enumerate(CASES, 1):
        rel = f"responses/{i:02d}-{name}.txt"
        (wd / rel).write_text(text, encoding="utf-8")
        prompt_rel = f"full/{name}.md"
        (wd / prompt_rel).write_text(f"prompt for {name}", encoding="utf-8")
        run_manifest.append({"run": i, "task_id": "dependency-anchor-01",
                             "variant": "full", "prompt": prompt_rel, "response": rel})
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
    by_name = {}
    for (name, _, expect), row in zip(CASES, rows):
        by_name[name] = row
        for key, value in expect.items():
            assert row[key] == value, f"{name}: {key}={row[key]!r}, expected {value!r}"
    for name, marker in FORMAT_VIOLATION_MARKERS.items():
        assert marker in by_name[name]["format_violations"], \
            f"{name}: {marker!r} not in {by_name[name]['format_violations']!r}"
    forbidden_row = by_name["forbidden-write"]
    assert forbidden_row["protocol_violations"] == ["requirements.txt"], forbidden_row
    assert forbidden_row["forbidden_path_changes"] == [], forbidden_row
    # The "good" case is the only fully compliant row.
    assert [r["format_violations"] for r in rows if r["format_compliant"]] == [[]]

    aggregate = json.loads((wd / "aggregate-edit-content.json").read_text(encoding="utf-8"))
    assert aggregate["summary"]["full"]["semantic_task_success"] == 3, aggregate["summary"]
    assert aggregate["summary"]["full"]["task_success"] == 1, aggregate["summary"]
    assert aggregate["summary"]["full"]["format_compliant"] == 1, aggregate["summary"]

print("edit-content parser+scorer self-test: PASS")
