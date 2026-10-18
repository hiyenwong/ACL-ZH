#!/usr/bin/env python3
"""Reproducibility self-test for provenance capture (P2-02).

Must hold:
- file hashes are over exact bytes; a missing file hashes to None;
- the prompt-bundle hash is sensitive to run order;
- scoring with a generation-time baseline that matches the actual
  inputs is "verified" (score_kind "initial");
- scoring with a tampered manifest fails closed without the override;
- with --allow-version-mismatch the same tampered run scores as
  "mismatch_overridden" (score_kind "rescore") and preserves both the
  recorded and actual hashes;
- scoring a run whose generation metadata predates provenance capture
  is labeled "unpinned_baseline" (score_kind "rescore"), not an error.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK = HERE.parents[0]

spec = importlib.util.spec_from_file_location("provenance", HERE / "provenance.py")
prov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prov)

# --- unit checks ---
assert prov.sha256_file(HERE / "does-not-exist.xyz") is None
assert prov.sha256_file(HERE / "provenance.py") is not None

with tempfile.TemporaryDirectory(prefix="aclzh-prov-unit-") as td:
    root = Path(td)
    (root / "a.md").write_text("aaa", encoding="utf-8")
    (root / "b.md").write_text("bbb", encoding="utf-8")
    m1 = [{"prompt": "a.md"}, {"prompt": "b.md"}]
    m2 = [{"prompt": "b.md"}, {"prompt": "a.md"}]
    assert prov.prompt_bundle_sha256(root, m1) != prov.prompt_bundle_sha256(root, m2)
    try:
        prov.prompt_bundle_sha256(root, [{"prompt": "missing.md"}])
        raise AssertionError("missing prompt file must raise")
    except FileNotFoundError:
        pass

# --- end-to-end checks through the edit-content scorer ---
MANIFEST = BENCHMARK / "tasks" / "manifest-dependency-mirror-v0.4.jsonl"
SCORER = HERE / "score_edit_content_run.py"

CORRECT = ("<<<FILE:src/serializer.py>>>\n"
           "import json\n\n"
           "def dumps(value):\n"
           "    return json.dumps(value, sort_keys=True, separators=(',', ':'))\n"
           "<<<END>>>")


def run_scorer(wd, manifest, extra=()):
    return subprocess.run(
        [sys.executable, str(SCORER), "--workdir", str(wd),
         "--experiment", str(wd / "experiment.json"), "--manifest", str(manifest),
         *extra],
        capture_output=True, text=True)


def read_aggregate(wd):
    return json.loads((wd / "aggregate-edit-content.json").read_text(encoding="utf-8"))


with tempfile.TemporaryDirectory(prefix="aclzh-prov-e2e-") as td:
    wd = Path(td)
    # Write experiment.json first so the baseline can hash it.
    (wd / "experiment.json").write_text(json.dumps(
        {"experiment_id": "selftest-provenance", "variants": ["full"]}), encoding="utf-8")
    (wd / "full").mkdir()
    (wd / "full" / "dependency-anchor-01-full.md").write_text("prompt", encoding="utf-8")
    (wd / "responses").mkdir()
    (wd / "responses" / "01.txt").write_text(CORRECT, encoding="utf-8")
    run_manifest = [{"run": 1, "task_id": "dependency-anchor-01", "variant": "full",
                     "prompt": "full/dependency-anchor-01-full.md",
                     "response": "responses/01.txt"}]
    (wd / "run-manifest.json").write_text(json.dumps(run_manifest), encoding="utf-8")
    baseline = prov.generation_provenance(
        manifest=MANIFEST, experiment=wd / "experiment.json",
        exporter=HERE / "export_edit_content_prompts.py",
        workdir=wd, run_manifest=run_manifest,
    )

    # 1. verified baseline
    (wd / "generation-metadata.json").write_text(
        json.dumps({"model": "selftest", "provenance": baseline}), encoding="utf-8")
    res = run_scorer(wd, MANIFEST)
    assert res.returncode == 0, res.stderr
    agg = read_aggregate(wd)
    assert agg["provenance"]["status"] == "verified", agg["provenance"]
    assert agg["provenance"]["score_kind"] == "initial", agg["provenance"]
    assert agg["provenance"]["actual"]["scorer_sha256"], agg["provenance"]
    assert agg["provenance"]["actual"]["parser_sha256"], agg["provenance"]
    assert agg["provenance"]["actual"]["oracle_sha256"], agg["provenance"]

    # 2. tampered manifest fails closed
    tampered = wd / "manifest-tampered.jsonl"
    tampered.write_text(MANIFEST.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    res = run_scorer(wd, tampered)
    assert res.returncode != 0, "tampered manifest must fail closed"
    assert "manifest_sha256" in res.stderr, res.stderr

    # 3. override labels the score a rescore and preserves both hashes
    res = run_scorer(wd, tampered, extra=["--allow-version-mismatch"])
    assert res.returncode == 0, res.stderr
    agg = read_aggregate(wd)
    p = agg["provenance"]
    assert p["status"] == "mismatch_overridden", p
    assert p["score_kind"] == "rescore", p
    mm = p["mismatches"]["manifest_sha256"]
    assert mm["recorded"] == baseline["manifest_sha256"], p
    assert mm["actual"] == prov.sha256_file(tampered), p

    # 4. generation metadata without provenance: unpinned baseline rescore
    (wd / "generation-metadata.json").write_text(
        json.dumps({"model": "selftest"}), encoding="utf-8")
    res = run_scorer(wd, MANIFEST)
    assert res.returncode == 0, res.stderr
    agg = read_aggregate(wd)
    assert agg["provenance"]["status"] == "unpinned_baseline", agg["provenance"]
    assert agg["provenance"]["score_kind"] == "rescore", agg["provenance"]

print("provenance self-test: PASS")
