"""Resumable local runner for the frozen d12 nanochat suppression study."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

BASE_MODEL_TAG = "d12-supp"
ARMS = ("trace", "direct")
EXPECTED_SFT_STEPS = {"trace": 62, "direct": 40}
EVAL_PROMPTS = 400
BASE_STEPS = 5000
NANOCHAT_COMMIT = "92d63d4e8bb4df75c3b71618f31ddde2378b2bcd"


@dataclass(frozen=True)
class PipelinePaths:
    repo: Path
    nanochat: Path
    artifacts: Path
    cache: Path

    @property
    def python(self) -> Path:
        return self.nanochat / ".venv/bin/python"

    @property
    def base_checkpoint_dir(self) -> Path:
        return self.cache / "base_checkpoints" / BASE_MODEL_TAG

    def arm_base_checkpoint_dir(self, arm: str) -> Path:
        return self.cache / "base_checkpoints" / f"{BASE_MODEL_TAG}-{arm}"

    def sft_checkpoint_dir(self, arm: str) -> Path:
        return self.cache / "chatsft_checkpoints" / f"{BASE_MODEL_TAG}-{arm}"

    @property
    def eval_set_path(self) -> Path:
        return self.artifacts / "eval-set.jsonl"

    def eval_output_path(self, arm: str) -> Path:
        return self.artifacts / f"eval-d12-{arm}.jsonl"

    def eval_summary_path(self, arm: str) -> Path:
        return self.eval_output_path(arm).with_suffix(".summary.json")

    @property
    def report_path(self) -> Path:
        return self.artifacts / "d12-suppression-report.json"


Runner = Callable[[list[str], str, dict[str, str], Path], None]


def latest_checkpoint_step(checkpoint_dir: Path) -> int:
    """Return the newest step with model, optimizer, and metadata files."""
    steps = []
    for meta_path in checkpoint_dir.glob("meta_*.json"):
        step = int(meta_path.stem.removeprefix("meta_"))
        model_path = checkpoint_dir / f"model_{step:06d}.pt"
        optimizer_path = checkpoint_dir / f"optim_{step:06d}_rank0.pt"
        if model_path.is_file() and optimizer_path.is_file():
            steps.append(step)
    return max(steps, default=-1)


def base_command(python: Path, resume_step: int) -> list[str]:
    """Build the frozen base-training command, resuming optimizer state."""
    return [
        "caffeinate",
        "-dims",
        str(python),
        "-m",
        "scripts.base_train",
        "--depth=12",
        "--head-dim=64",
        "--window-pattern=L",
        "--max-seq-len=512",
        "--device-batch-size=32",
        "--total-batch-size=16384",
        "--eval-every=100",
        "--eval-tokens=524288",
        "--core-metric-every=-1",
        "--sample-every=-1",
        "--save-every=500",
        "--num-iterations=5000",
        "--run=dummy",
        f"--model-tag={BASE_MODEL_TAG}",
        f"--resume-from-step={resume_step}",
    ]


def sft_command(python: Path, arm: str) -> list[str]:
    """Build one example-matched SFT arm; the dataset ends the epoch."""
    if arm not in ARMS:
        raise ValueError(f"Unknown arm: {arm}")
    return [
        "caffeinate",
        "-dims",
        str(python),
        "-m",
        "scripts.chat_sft",
        "--num-iterations=1500",
        "--eval-every=-1",
        "--chatcore-every=-1",
        "--run=dummy",
        f"--model-tag={BASE_MODEL_TAG}-{arm}",
    ]


def eval_command(
    python: Path, script: Path, arm: str, eval_set: Path, out: Path
) -> list[str]:
    return [
        "caffeinate",
        "-dims",
        str(python),
        str(script),
        "--model-tag",
        f"{BASE_MODEL_TAG}-{arm}",
        "--eval-set",
        str(eval_set),
        "--out",
        str(out),
        "--max-tokens",
        "160",
    ]


def summarize_command(python: Path, paths: PipelinePaths) -> list[str]:
    script = paths.repo / "benchmark/local-model/nanochat/summarize_suppression.py"
    return [
        str(python),
        str(script),
        "--trace-summary",
        str(paths.eval_summary_path("trace")),
        "--direct-summary",
        str(paths.eval_summary_path("direct")),
        "--out",
        str(paths.report_path),
    ]


def evaluation_complete(summary_path: Path) -> bool:
    """Check that an existing evaluation contains every frozen prompt."""
    if not summary_path.exists():
        return False
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return summary.get("overall", {}).get("n") == EVAL_PROMPTS


def emit_progress(phase: str, step: int, total: int, unit: str) -> None:
    payload = {"phase": phase, "step": step, "of": total, "unit": unit}
    print(f"::orx:: {json.dumps(payload)}", flush=True)


def run_logged(command: list[str], phase: str, env: dict[str, str], cwd: Path) -> None:
    """Stream a subprocess into the immutable run log with a phase prefix."""
    print(f"=== {phase}: {' '.join(command)} ===", flush=True)
    with subprocess.Popen(
        command,
        cwd=cwd,
        env={**os.environ, **env},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as process:
        assert process.stdout is not None
        for line in process.stdout:
            print(f"[{phase}] {line.rstrip()}", flush=True)
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, command)


def copy_final_checkpoint(paths: PipelinePaths, arm: str) -> None:
    """Copy only the final base state needed by SFT into its arm tag."""
    source = paths.base_checkpoint_dir
    destination = paths.arm_base_checkpoint_dir(arm)
    destination.mkdir(parents=True, exist_ok=True)
    for filename in (
        f"model_{BASE_STEPS:06d}.pt",
        f"optim_{BASE_STEPS:06d}_rank0.pt",
        f"meta_{BASE_STEPS:06d}.json",
    ):
        shutil.copy2(source / filename, destination / filename)


def pipeline_env(paths: PipelinePaths, arm: str | None = None) -> dict[str, str]:
    env = {
        "PYTHONPATH": str(paths.repo / "benchmark/local-model/nanochat"),
        "PYTHONUNBUFFERED": "1",
        "WANDB_MODE": "disabled",
        "NANOCHAT_SUPP_TRAIN_ITEMS": "0",
        "NANOCHAT_BASE_DIR": str(paths.cache),
    }
    if arm is not None:
        env["NANOCHAT_SUPP_ARM"] = arm
        env["NANOCHAT_SFT_TASKS"] = "suppression_arith"
    return env


def execute_pipeline(paths: PipelinePaths, runner: Runner = run_logged) -> None:
    """Resume incomplete stages and execute the frozen d12 arm protocol."""
    paths.artifacts.mkdir(parents=True, exist_ok=True)
    resume_step = latest_checkpoint_step(paths.base_checkpoint_dir)
    if resume_step < 0:
        raise FileNotFoundError(
            f"No complete base checkpoint in {paths.base_checkpoint_dir}"
        )
    if resume_step > BASE_STEPS:
        raise ValueError(f"Unexpected base checkpoint step: {resume_step}")
    emit_progress("train", resume_step, BASE_STEPS, "steps")
    if resume_step < BASE_STEPS:
        runner(
            base_command(paths.python, resume_step),
            "train",
            pipeline_env(paths),
            paths.nanochat,
        )
    if latest_checkpoint_step(paths.base_checkpoint_dir) != BASE_STEPS:
        raise RuntimeError("Base training did not produce the step-5000 checkpoint")
    emit_progress("train", BASE_STEPS, BASE_STEPS, "steps")

    for arm in ARMS:
        expected = EXPECTED_SFT_STEPS[arm]
        if latest_checkpoint_step(paths.arm_base_checkpoint_dir(arm)) != BASE_STEPS:
            copy_final_checkpoint(paths, arm)
        sft_step = latest_checkpoint_step(paths.sft_checkpoint_dir(arm))
        if sft_step not in (-1, expected):
            raise ValueError(f"Unexpected {arm} SFT checkpoint step: {sft_step}")
        emit_progress(f"sft-{arm}", max(sft_step, 0), expected, "steps")
        if sft_step == -1:
            runner(
                sft_command(paths.python, arm),
                f"sft-{arm}",
                pipeline_env(paths, arm),
                paths.nanochat,
            )
        if latest_checkpoint_step(paths.sft_checkpoint_dir(arm)) != expected:
            raise RuntimeError(f"{arm} SFT did not produce the epoch-end checkpoint")
        emit_progress(f"sft-{arm}", expected, expected, "steps")

    eval_script = paths.repo / "benchmark/local-model/nanochat/eval_suppression.py"
    for arm in ARMS:
        complete = evaluation_complete(paths.eval_summary_path(arm))
        emit_progress(
            f"eval-{arm}", EVAL_PROMPTS if complete else 0, EVAL_PROMPTS, "prompts"
        )
        if not complete:
            runner(
                eval_command(
                    paths.python,
                    eval_script,
                    arm,
                    paths.eval_set_path,
                    paths.eval_output_path(arm),
                ),
                f"eval-{arm}",
                pipeline_env(paths),
                paths.nanochat,
            )
        if not evaluation_complete(paths.eval_summary_path(arm)):
            raise RuntimeError(
                f"{arm} evaluation did not complete all {EVAL_PROMPTS} prompts"
            )
        emit_progress(f"eval-{arm}", EVAL_PROMPTS, EVAL_PROMPTS, "prompts")

    emit_progress("summarize", 0, 1, "report")
    runner(
        summarize_command(paths.python, paths),
        "summarize",
        pipeline_env(paths),
        paths.nanochat,
    )
    if not paths.report_path.is_file():
        raise RuntimeError("Summary report was not written")
    emit_progress("summarize", 1, 1, "report")


def flatten_report(report: dict) -> dict[str, float]:
    """Map the preregistered arm endpoints to stable run signal names."""
    metrics: dict[str, float] = {}
    for arm, report_arm in (("trace", "trace-trained"), ("direct", "direct-trained")):
        summary = report["arms"][report_arm]
        metrics[f"{arm}_silent_accuracy"] = summary["by_mode"]["direct"]["accuracy"]
        metrics[f"{arm}_visible_accuracy"] = summary["by_mode"]["trace"]["accuracy"]
        metrics[f"{arm}_leak_rate"] = summary["by_mode"]["direct"][
            "leak_rate_prefix_chars_gt_0"
        ]
        multi = summary["by_mode_and_size"]["direct_multi"]
        metrics[f"{arm}_silent_multi_accuracy"] = multi["accuracy"]
        metrics[f"{arm}_silent_multi_error"] = multi["mean_abs_error_wrong"]
    return metrics


def default_paths() -> PipelinePaths:
    repo = Path(__file__).resolve().parents[2]
    artifact_default = (
        Path.home() / ".local/share/openresearch/files/acl-zh/nanochat-artifacts"
    )
    nanochat_default = artifact_default.parent / "nanochat-src"
    return PipelinePaths(
        repo=repo,
        nanochat=Path(os.environ.get("NANOCHAT_ROOT", nanochat_default)),
        artifacts=Path(os.environ.get("NANOCHAT_ARTIFACT_ROOT", artifact_default)),
        cache=Path(
            os.environ.get(
                "NANOCHAT_BASE_DIR",
                os.environ.get("NANOCHAT_CACHE", Path.home() / ".cache/nanochat"),
            )
        ),
    )


def validate_environment(paths: PipelinePaths) -> None:
    if not paths.python.is_file():
        raise FileNotFoundError(f"Missing nanochat Python: {paths.python}")
    if shutil.which("caffeinate") is None:
        raise FileNotFoundError(
            "caffeinate is required to prevent sleep during training"
        )
    rows = paths.eval_set_path.read_text(encoding="utf-8").splitlines()
    if len(rows) != EVAL_PROMPTS:
        raise ValueError(f"Expected {EVAL_PROMPTS} eval prompts, found {len(rows)}")
    commit = subprocess.run(
        ["git", "-C", str(paths.nanochat), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if commit != NANOCHAT_COMMIT:
        raise ValueError(f"Unexpected nanochat commit: {commit}")
    sft_script = paths.nanochat / "scripts/chat_sft.py"
    if "NANOCHAT_SFT_TASKS" not in sft_script.read_text(encoding="utf-8"):
        raise ValueError(f"Missing external SFT mixture patch: {sft_script}")


def main() -> None:
    paths = default_paths()
    emit_progress("setup", 0, 1, "checks")
    validate_environment(paths)
    resume_step = latest_checkpoint_step(paths.base_checkpoint_dir)
    print(
        "FROZEN CONFIG "
        + json.dumps(
            {
                "nanochat_commit": NANOCHAT_COMMIT,
                "base_resume_step": resume_step,
                "base_steps": BASE_STEPS,
                "sft_steps": EXPECTED_SFT_STEPS,
                "eval_prompts_per_arm": EVAL_PROMPTS,
            }
        ),
        flush=True,
    )
    emit_progress("setup", 1, 1, "checks")
    execute_pipeline(paths)
    report = json.loads(paths.report_path.read_text(encoding="utf-8"))
    metrics = flatten_report(report)
    for arm in ARMS:
        row = {"arm": arm}
        row.update(
            {
                key.removeprefix(f"{arm}_"): value
                for key, value in metrics.items()
                if key.startswith(f"{arm}_")
            }
        )
        print(f"::orx:: {json.dumps({'row': 'arms', 'm': row})}", flush=True)
    print(f"::orx:: {json.dumps({'m': metrics})}", flush=True)
    print("FINAL SUMMARY d12 " + json.dumps(metrics), flush=True)
    print(f"ARTIFACTS {paths.artifacts}", flush=True)


if __name__ == "__main__":
    main()
