#!/usr/bin/env python3
"""Fail-closed construction audit for the information-equivalent manifest."""
import argparse
import importlib.util
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("baseline", "minimal", "full")
OLD_TASK_IDS = (
    "dependency-anchor-01", "dependency-no-file-ban-01",
    "dependency-no-target-file-01", "dependency-verbose-01", "scope-01",
    "dependency-01", "exception-01", "compatibility-01",
    "constraint-path-01", "constraint-stdlib-01", "constraint-schema-01",
    "constraint-side-effect-01", "constraint-retry-01",
    "constraint-immutable-01", "constraint-return-01", "constraint-api-01",
)
GENERIC_LINES = {
    "请按下方事实完成任务。", "必要事实：", "修改范围：", "评估方式：",
    "完成任务。", "事实：", "范围：", "评估：",
    "# 任务", "目标：满足全部原子事实。", "## 原子事实", "## 范围", "## 评估",
}
REFERENCE_MARKERS = {
    "eq-slug-01": "slugify",
    "eq-clock-01": "format_clock",
    "eq-order-01": "ordered_tags",
    "eq-settings-01": "build_settings",
    "eq-score-01": "validate_score",
    "eq-quiet-01": "record(at)",
    "eq-money-01": "format_amount",
    "eq-month-01": "month_name",
    "eq-fallback-01": "first_value",
    "eq-clamp-01": "clamp(value",
    "eq-window-01": "src/window.py",
    "eq-retry-01": "bounded_retry",
}


def load_manifest(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def audit(manifest_path):
    tasks = load_manifest(manifest_path)
    errors = []
    task_ids = [task.get("id") for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        errors.append("task IDs are not unique")
    if set(task_ids) & set(OLD_TASK_IDS):
        errors.append(f"old tuning task IDs reused: {sorted(set(task_ids) & set(OLD_TASK_IDS))}")

    all_fact_ids = []
    task_results = []
    with tempfile.TemporaryDirectory(prefix="aclzh-equivalence-audit-") as temp:
        spec = importlib.util.spec_from_file_location("aclzh_runner", ROOT / "agent-eval/run.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        fixture_dir = Path(temp)
        runner.write_fixture(fixture_dir)
        oracle_source = (ROOT / "agent-eval/run.py").read_text(encoding="utf-8")
        reference_source = (ROOT / "agent-eval/reference_agent.py").read_text(encoding="utf-8")

        for task in tasks:
            task_id = task.get("id", "<unknown>")
            local_errors = []
            if task.get("schema_version") != "information-equivalent-task-v0.1":
                local_errors.append("wrong schema_version")
            if task.get("fixture") != "synthetic-python-equivalence-v0.1":
                local_errors.append("wrong fixture")
            if task.get("difficulty") not in {"simple", "moderate", "hard"}:
                local_errors.append("invalid difficulty")

            fact_records = task.get("atomic_facts", [])
            fact_ids = [fact.get("id") for fact in fact_records]
            all_fact_ids.extend(fact_ids)
            if len(fact_ids) != len(set(fact_ids)):
                local_errors.append("duplicate atomic fact IDs")
            if any(not fact_id or not fact_id.startswith(f"{task_id}/F") for fact_id in fact_ids):
                local_errors.append("atomic fact ID prefix mismatch")
            if any(fact.get("hardness") != "required" for fact in fact_records):
                local_errors.append("atomic fact hardness is not uniformly required")
            if any(fact.get("counted") is not True for fact in fact_records):
                local_errors.append("an atomic fact is not counted")
            if any(not str(fact.get("oracle_assertion", "")).strip() for fact in fact_records):
                local_errors.append("atomic fact lacks oracle assertion")

            scope_records = task.get("scope_facts", [])
            eval_records = task.get("evaluation_facts", [])
            if len(scope_records) != 1 or len(eval_records) != 1:
                local_errors.append("scope/evaluation fact count must be exactly one")
            required_lines = [f"[{fact.get('id')}] {fact.get('text')}" for fact in fact_records]
            if scope_records:
                required_lines.append(scope_records[0].get("text", ""))
            if eval_records:
                if eval_records[0].get("counted") is not False:
                    local_errors.append("evaluation disclosure must be uncounted")
                required_lines.append(eval_records[0].get("text", ""))

            variants = {}
            for variant in VARIANTS:
                prompt = task.get(variant)
                if not isinstance(prompt, str):
                    local_errors.append(f"{variant} prompt missing")
                    continue
                variants[variant] = prompt
                for line in required_lines:
                    if line not in prompt:
                        local_errors.append(f"{variant} missing required line: {line}")
                if "python -m unittest" in prompt or "运行 python -m unittest" in prompt:
                    local_errors.append(f"{variant} instructs the model to run tests")
                if any(old_id in prompt for old_id in OLD_TASK_IDS):
                    local_errors.append(f"{variant} mentions an old task ID")
                remaining = [line for line in prompt.splitlines() if line and line not in set(required_lines)]
                extras = [line for line in remaining if line not in GENERIC_LINES]
                if extras:
                    local_errors.append(f"{variant} has variant-only content: {extras}")
            if len(set(variants.values())) != len(variants):
                local_errors.append("variant prompts are not all distinct")

            allowed = task.get("allowed_paths", [])
            if len(allowed) != 1 or not allowed[0].startswith("src/"):
                local_errors.append("allowed_paths must contain exactly one src file")
            elif not (fixture_dir / allowed[0]).exists():
                local_errors.append(f"fixture source missing: {allowed[0]}")
            if task.get("forbidden_paths") != []:
                local_errors.append("forbidden_paths must be empty for this manifest")
            if f'if task_id == "{task_id}"' not in oracle_source:
                local_errors.append("hidden oracle branch missing")
            marker = REFERENCE_MARKERS.get(task_id)
            if marker and marker not in reference_source:
                local_errors.append("reference implementation marker missing")

            task_results.append({
                "id": task_id,
                "facts": len(fact_records),
                "required_lines_found": not any("missing required line" in error for error in local_errors),
                "variant_only_content": any("variant-only content" in error for error in local_errors),
                "errors": local_errors,
            })
            if local_errors:
                errors.extend([f"{task_id}: {error}" for error in local_errors])

    if len(all_fact_ids) != len(set(all_fact_ids)):
        errors.append("atomic fact IDs are not globally unique")
    result = {
        "manifest": str(Path(manifest_path).resolve()),
        "schema_version": "information-equivalent-task-v0.1",
        "task_count": len(tasks),
        "atomic_fact_count": len(all_fact_ids),
        "strict_equivalence_pass": not errors,
        "tasks": task_results,
        "errors": errors,
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    result = audit(args.manifest)
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "task_count": result["task_count"],
        "atomic_fact_count": result["atomic_fact_count"],
        "strict_equivalence_pass": result["strict_equivalence_pass"],
        "error_count": len(result["errors"]),
    }, ensure_ascii=False))
    if result["errors"]:
        for error in result["errors"]:
            print("ERROR", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
