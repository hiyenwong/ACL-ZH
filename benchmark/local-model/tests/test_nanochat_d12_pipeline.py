"""Unit tests for the resumable d12 suppression experiment pipeline."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "nanochat_d12_pipeline.py"


def load_pipeline():
    spec = importlib.util.spec_from_file_location("nanochat_d12_pipeline", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_checkpoint(directory: Path, step: int, *, optimizer: bool = True) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"model_{step:06d}.pt").touch()
    (directory / f"meta_{step:06d}.json").write_text("{}", encoding="utf-8")
    if optimizer:
        (directory / f"optim_{step:06d}_rank0.pt").touch()


def test_latest_checkpoint_ignores_incomplete_files(tmp_path: Path) -> None:
    pipeline = load_pipeline()
    for step in (500, 1000, 2000):
        write_checkpoint(tmp_path, step)
    write_checkpoint(tmp_path, 2500, optimizer=False)

    assert pipeline.latest_checkpoint_step(tmp_path) == 2000


def test_latest_checkpoint_returns_minus_one_without_checkpoints(
    tmp_path: Path,
) -> None:
    pipeline = load_pipeline()

    assert pipeline.latest_checkpoint_step(tmp_path) == -1


def test_base_command_resumes_with_frozen_training_settings() -> None:
    pipeline = load_pipeline()

    command = pipeline.base_command(Path("/venv/bin/python"), 2000)

    assert command[:4] == ["caffeinate", "-dims", "/venv/bin/python", "-m"]
    assert "scripts.base_train" in command
    assert "--resume-from-step=2000" in command
    assert "--num-iterations=5000" in command
    assert "--depth=12" in command
    assert "--save-every=500" in command
    assert "--model-tag=d12-supp" in command


def test_sft_command_keeps_one_epoch_protocol() -> None:
    pipeline = load_pipeline()

    command = pipeline.sft_command(Path("/venv/bin/python"), "trace")

    assert "scripts.chat_sft" in command
    assert "--num-iterations=1500" in command
    assert "--eval-every=-1" in command
    assert "--chatcore-every=-1" in command
    assert "--model-tag=d12-supp-trace" in command


def test_eval_command_uses_module_import_from_nanochat_checkout() -> None:
    pipeline = load_pipeline()

    command = pipeline.eval_command(
        Path("/venv/bin/python"),
        Path("/repo/eval_suppression.py"),
        "trace",
        Path("/eval.jsonl"),
        Path("/out.jsonl"),
    )

    assert command[3:5] == ["-m", "eval_suppression"]
    assert "--model-tag" in command
    assert "d12-supp-trace" in command


def test_evaluation_complete_requires_all_400_rows(tmp_path: Path) -> None:
    pipeline = load_pipeline()
    summary = tmp_path / "eval.summary.json"

    assert not pipeline.evaluation_complete(summary)
    summary.write_text(json.dumps({"overall": {"n": 200}}), encoding="utf-8")
    assert not pipeline.evaluation_complete(summary)
    summary.write_text(json.dumps({"overall": {"n": 400}}), encoding="utf-8")
    assert pipeline.evaluation_complete(summary)


def test_invalid_evaluation_summary_is_treated_as_incomplete(tmp_path: Path) -> None:
    pipeline = load_pipeline()
    summary = tmp_path / "eval.summary.json"
    summary.write_text("not json", encoding="utf-8")

    assert not pipeline.evaluation_complete(summary)


def make_paths(tmp_path: Path):
    pipeline = load_pipeline()
    return pipeline, pipeline.PipelinePaths(
        repo=tmp_path / "repo",
        nanochat=tmp_path / "nanochat",
        artifacts=tmp_path / "artifacts",
        cache=tmp_path / "cache",
    )


def test_pipeline_resumes_then_runs_arms_in_frozen_order(tmp_path: Path) -> None:
    pipeline, paths = make_paths(tmp_path)
    write_checkpoint(paths.base_checkpoint_dir, 2000)
    calls = []

    def fake_runner(command, phase, env, cwd):
        calls.append((command, phase, env, cwd))
        if phase == "train":
            write_checkpoint(paths.base_checkpoint_dir, 5000)
        elif phase.startswith("sft-"):
            arm = phase.removeprefix("sft-")
            write_checkpoint(
                paths.sft_checkpoint_dir(arm), pipeline.EXPECTED_SFT_STEPS[arm]
            )
        elif phase.startswith("eval-"):
            arm = phase.removeprefix("eval-")
            paths.eval_summary_path(arm).write_text(
                json.dumps({"overall": {"n": 400}}), encoding="utf-8"
            )
        elif phase == "summarize":
            paths.report_path.write_text("{}", encoding="utf-8")

    pipeline.execute_pipeline(paths, runner=fake_runner)

    assert [call[1] for call in calls] == [
        "train",
        "sft-trace",
        "sft-direct",
        "eval-trace",
        "eval-direct",
        "summarize",
    ]
    assert "--resume-from-step=2000" in calls[0][0]
    assert calls[1][2]["NANOCHAT_SUPP_ARM"] == "trace"
    assert calls[2][2]["NANOCHAT_SUPP_ARM"] == "direct"
    assert (
        pipeline.latest_checkpoint_step(paths.arm_base_checkpoint_dir("trace")) == 5000
    )
    assert (
        pipeline.latest_checkpoint_step(paths.arm_base_checkpoint_dir("direct")) == 5000
    )


def test_pipeline_skips_completed_training_and_evaluation(tmp_path: Path) -> None:
    pipeline, paths = make_paths(tmp_path)
    write_checkpoint(paths.base_checkpoint_dir, 5000)
    for arm in pipeline.ARMS:
        write_checkpoint(
            paths.sft_checkpoint_dir(arm), pipeline.EXPECTED_SFT_STEPS[arm]
        )
        paths.eval_summary_path(arm).parent.mkdir(parents=True, exist_ok=True)
        paths.eval_summary_path(arm).write_text(
            json.dumps({"overall": {"n": 400}}), encoding="utf-8"
        )
    calls = []

    def fake_runner(command, phase, env, cwd):
        calls.append(phase)
        paths.report_path.write_text("{}", encoding="utf-8")

    pipeline.execute_pipeline(paths, runner=fake_runner)

    assert calls == ["summarize"]


def test_run_logged_prefixes_subprocess_output(tmp_path: Path, capsys) -> None:
    pipeline = load_pipeline()

    pipeline.run_logged(["/bin/echo", "hello"], phase="check", env={}, cwd=tmp_path)

    assert "[check] hello" in capsys.readouterr().out


def test_flatten_report_exposes_preregistered_endpoints() -> None:
    pipeline = load_pipeline()
    report = {
        "arms": {
            "trace-trained": {
                "by_mode": {
                    "direct": {"accuracy": 0.7, "leak_rate_prefix_chars_gt_0": 0.0},
                    "trace": {"accuracy": 1.0},
                },
                "by_mode_and_size": {
                    "direct_multi": {"accuracy": 0.6, "mean_abs_error_wrong": 1.5}
                },
            },
            "direct-trained": {
                "by_mode": {
                    "direct": {"accuracy": 0.8, "leak_rate_prefix_chars_gt_0": 0.0},
                    "trace": {"accuracy": 0.75},
                },
                "by_mode_and_size": {
                    "direct_multi": {"accuracy": 0.65, "mean_abs_error_wrong": 2.5}
                },
            },
        }
    }

    metrics = pipeline.flatten_report(report)

    assert metrics["trace_silent_accuracy"] == 0.7
    assert metrics["trace_visible_accuracy"] == 1.0
    assert metrics["trace_silent_multi_accuracy"] == 0.6
    assert metrics["trace_silent_multi_error"] == 1.5
    assert metrics["direct_silent_accuracy"] == 0.8
    assert metrics["direct_visible_accuracy"] == 0.75
    assert metrics["direct_silent_multi_accuracy"] == 0.65
    assert metrics["direct_silent_multi_error"] == 2.5


def test_default_paths_honor_environment_overrides(tmp_path: Path, monkeypatch) -> None:
    pipeline = load_pipeline()
    monkeypatch.setenv("NANOCHAT_ROOT", str(tmp_path / "src"))
    monkeypatch.setenv("NANOCHAT_ARTIFACT_ROOT", str(tmp_path / "out"))
    monkeypatch.setenv("NANOCHAT_CACHE", str(tmp_path / "cache"))

    paths = pipeline.default_paths()

    assert paths.nanochat == tmp_path / "src"
    assert paths.artifacts == tmp_path / "out"
    assert paths.cache == tmp_path / "cache"
    assert paths.repo == MODULE_PATH.parents[2]


def test_main_finishes_setup_before_pipeline(tmp_path: Path, monkeypatch) -> None:
    pipeline = load_pipeline()
    _, paths = make_paths(tmp_path)
    paths.artifacts.mkdir(parents=True)
    paths.report_path.write_text("{}", encoding="utf-8")
    write_checkpoint(paths.base_checkpoint_dir, 2000)
    events = []
    monkeypatch.setattr(pipeline, "default_paths", lambda: paths)
    monkeypatch.setattr(pipeline, "validate_environment", lambda paths: None)
    monkeypatch.setattr(pipeline, "flatten_report", lambda report: {})
    monkeypatch.setattr(
        pipeline, "execute_pipeline", lambda paths: events.append("pipeline")
    )
    monkeypatch.setattr(
        pipeline,
        "emit_progress",
        lambda phase, step, total, unit: events.append(f"{phase}:{step}"),
    )

    pipeline.main()

    assert events == ["setup:0", "setup:1", "pipeline"]


def test_native_cache_override_is_forwarded_to_subprocesses(
    tmp_path: Path, monkeypatch
) -> None:
    pipeline = load_pipeline()
    monkeypatch.setenv("NANOCHAT_BASE_DIR", str(tmp_path / "native"))
    monkeypatch.setenv("NANOCHAT_CACHE", str(tmp_path / "legacy"))

    paths = pipeline.default_paths()

    assert paths.cache == tmp_path / "native"
    assert pipeline.pipeline_env(paths)["NANOCHAT_BASE_DIR"] == str(tmp_path / "native")


def test_loss_patterns_capture_nonfinite_values() -> None:
    patterns_path = MODULE_PATH.parent / "d12-suppression-patterns.json"
    patterns = json.loads(patterns_path.read_text(encoding="utf-8"))
    lines = [
        "[train] step 02001/05000 (40.02%) | loss: nan | lrm: 0.85",
        "[sft-trace] step 00010 (16.00%) | loss: inf | lrm: 1.00",
        "[sft-direct] step 00010 (25.00%) | loss: -inf | lrm: 1.00",
    ]

    for pattern, line in zip(patterns[:3], lines, strict=True):
        assert re.search(pattern["regex"], line), line


def test_validate_environment_requires_external_sft_patch(
    tmp_path: Path, monkeypatch
) -> None:
    pipeline, paths = make_paths(tmp_path)
    paths.python.parent.mkdir(parents=True)
    paths.python.touch()
    paths.artifacts.mkdir()
    paths.eval_set_path.write_text("\n" * pipeline.EVAL_PROMPTS, encoding="utf-8")
    script = paths.nanochat / "scripts/chat_sft.py"
    script.parent.mkdir(parents=True)
    script.write_text("standard nanochat mixture", encoding="utf-8")
    monkeypatch.setattr(pipeline.shutil, "which", lambda name: "/usr/bin/caffeinate")
    monkeypatch.setattr(
        pipeline.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=pipeline.NANOCHAT_COMMIT + "\n"),
    )

    with pytest.raises(ValueError, match="external SFT mixture patch"):
        pipeline.validate_environment(paths)
