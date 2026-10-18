"""Provenance hashing for local benchmark runs (P2-02 follow-up).

Purpose: make historical rescoring auditable. A result directory must be
able to answer "which exact task definition, scorer, oracle, parser,
exporter, and experiment configuration produced this result?"

Hashing algorithm (documented in LM-STUDIO-TEST-PLAN.md R8):

- File hashes: SHA-256 over the exact file bytes. A missing or
  unreadable file hashes to None (recorded as null); callers decide
  whether null is fatal for their use.
- prompt_bundle_sha256: SHA-256 over the concatenation, in run-manifest
  order, of each prompt entry as:
      <prompt relpath as UTF-8> + b"\\0" + <exact file bytes> + b"\\0"
  The run-manifest.json bytes are NOT part of the bundle hash (it has
  its own hash); the ordering comes from the manifest list order.
  A missing prompt file raises FileNotFoundError: hashing a partial
  bundle would silently produce a stable-looking but wrong hash.
- git values are best-effort: None when git is unavailable or the
  directory is not a repository. git_dirty is True when
  `git status --porcelain` reports any change, False when clean, None
  when undeterminable.

Scoring-time verification compares the hashes recorded at generation
time (generation-metadata.json "provenance" block) against the hashes
of the files actually used in the scoring pass:

- "verified": all compared keys present in the recorded baseline and
  equal to the actual hashes;
- "unpinned_baseline": the generation metadata carries no provenance
  block (e.g. runs generated before provenance capture existed) —
  scoring proceeds, but the score is labeled a rescore;
- "mismatch_overridden": recorded and actual hashes differ and the
  caller passed --allow-version-mismatch — scoring proceeds with both
  hash sets preserved and the score labeled a rescore;
- mismatch without the override: fail closed (SystemExit), because a
  silently accepted version skew is exactly what provenance exists to
  prevent.
"""
import hashlib
import subprocess
from pathlib import Path

COMPARE_KEYS = (
    "manifest_sha256",
    "experiment_sha256",
    "run_manifest_sha256",
    "prompt_bundle_sha256",
)


def sha256_file(path):
    """SHA-256 of exact file bytes, or None when unreadable."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _git(args):
    try:
        out = subprocess.run(["git"] + args, capture_output=True, text=True,
                             timeout=15)
        if out.returncode != 0:
            return None
        return out.stdout
    except Exception:
        return None


def git_head():
    out = _git(["rev-parse", "HEAD"])
    return out.strip() if out else None


def git_dirty():
    out = _git(["status", "--porcelain"])
    if out is None:
        return None
    return bool(out.strip())


def prompt_bundle_sha256(root, run_manifest):
    """Hash the exported prompt files in run order (see module docstring)."""
    root = Path(root)
    h = hashlib.sha256()
    for item in run_manifest:
        rel = item["prompt"]
        data = (root / rel).read_bytes()  # FileNotFoundError propagates
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(data)
        h.update(b"\0")
    return h.hexdigest()


def generation_provenance(manifest, experiment, exporter, workdir, run_manifest):
    """Provenance block recorded by run_lm_studio.py at generation time."""
    return {
        "git_sha": git_head(),
        "git_dirty": git_dirty(),
        "manifest_sha256": sha256_file(manifest),
        "experiment_sha256": sha256_file(experiment),
        "exporter_sha256": sha256_file(exporter),
        "run_manifest_sha256": sha256_file(Path(workdir) / "run-manifest.json"),
        "prompt_bundle_sha256": prompt_bundle_sha256(workdir, run_manifest),
    }


def scoring_provenance(workdir, run_manifest, manifest, experiment, extra):
    """Actual hashes of the inputs used in this scoring pass.

    extra: dict of track-specific file hashes, e.g. scorer/oracle/parser.
    """
    actual = {
        "git_sha": git_head(),
        "git_dirty": git_dirty(),
        "manifest_sha256": sha256_file(manifest),
        "experiment_sha256": sha256_file(experiment),
        "run_manifest_sha256": sha256_file(Path(workdir) / "run-manifest.json"),
        "prompt_bundle_sha256": prompt_bundle_sha256(workdir, run_manifest),
    }
    actual.update(extra)
    return actual


def verify_provenance(recorded, actual):
    """Compare a recorded generation-time baseline against actual hashes.

    Returns (status, mismatches, missing_baseline):
    - status: "verified" | "unpinned_baseline" | "mismatch"
    - mismatches: {key: {"recorded": ..., "actual": ...}} for compared
      keys that differ
    - missing_baseline: compared keys absent from the recorded baseline
    """
    if not recorded:
        return "unpinned_baseline", {}, list(COMPARE_KEYS)
    mismatches = {}
    missing = []
    for key in COMPARE_KEYS:
        if recorded.get(key) is None:
            missing.append(key)
            continue
        if recorded[key] != actual.get(key):
            mismatches[key] = {"recorded": recorded[key], "actual": actual.get(key)}
    if mismatches:
        return "mismatch", mismatches, missing
    if missing:
        return "unpinned_baseline", {}, missing
    return "verified", {}, []
