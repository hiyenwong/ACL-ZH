#!/usr/bin/env python3
"""Build the fresh information-equivalent edit-content manifest.

The manifest is generated from an explicit atomic-fact ledger so prompt variants
cannot accidentally gain or lose a requirement. Scope and evaluation facts are
rendered verbatim in every variant; only their section framing differs.
"""
import argparse
import json
from pathlib import Path


TASKS = [
    {
        "id": "eq-slug-01",
        "category": "equivalence-string",
        "difficulty": "simple",
        "allowed_path": "src/slug.py",
        "facts": [
            ("slugify(value) 保持单参数公开签名。", "signature == ['value']"),
            ("先去掉 value 首尾空白，再转换为小写。", "leading/trailing whitespace stripped and value lowercased"),
            ("value 内部的连续空白转换为一个连字符 -。", "internal whitespace runs become one hyphen"),
            ("slugify('  Hello   WORLD  \\t') 必须返回 'hello-world'。", "canonical input returns hello-world"),
        ],
    },
    {
        "id": "eq-clock-01",
        "category": "equivalence-format",
        "difficulty": "simple",
        "allowed_path": "src/clock.py",
        "facts": [
            ("format_clock(seconds) 保持单参数公开签名。", "signature == ['seconds']"),
            ("seconds 是非负 int 秒数。", "nonnegative integer seconds"),
            ("format_clock(0) 返回 '00:00'。", "zero formats as 00:00"),
            ("format_clock(65) 返回 '01:05'。", "65 formats as 01:05"),
            ("format_clock(3600) 返回 '60:00'。", "3600 formats as 60:00"),
            ("返回值必须是 str。", "return type is str"),
        ],
    },
    {
        "id": "eq-order-01",
        "category": "equivalence-collection",
        "difficulty": "simple",
        "allowed_path": "src/order_tags.py",
        "facts": [
            ("ordered_tags(values) 保持单参数公开签名。", "signature == ['values']"),
            ("返回值必须是 list。", "return type is list"),
            ("删除重复值，只保留每个值第一次出现的顺序。", "duplicates removed in first-occurrence order"),
            ("不得原地修改传入的 values。", "input sequence remains unchanged"),
        ],
    },
    {
        "id": "eq-settings-01",
        "category": "equivalence-config",
        "difficulty": "moderate",
        "allowed_path": "src/session_settings.py",
        "facts": [
            ("build_settings(settings) 保持单参数公开签名。", "signature == ['settings']"),
            ("返回一个新 dict，而不是传入对象本身。", "returns a distinct dict"),
            ("空 settings 的默认值为 mode='viewer' 且 page=1。", "empty settings default to viewer/page=1"),
            ("settings 中出现的键覆盖同名默认值，未出现的默认键保留。", "supplied keys override defaults"),
            ("不得原地修改传入的 settings。", "input dict remains unchanged"),
        ],
    },
    {
        "id": "eq-score-01",
        "category": "equivalence-validation",
        "difficulty": "moderate",
        "allowed_path": "src/score.py",
        "facts": [
            ("validate_score(value) 保持单参数公开签名。", "signature == ['value']"),
            ("value 为 0 或 100 时保持原 int 并返回。", "0 and 100 remain valid ints"),
            ("value 小于 0 或大于 100 时抛出 InvalidScoreError。", "out-of-range values raise InvalidScoreError"),
            ("InvalidScoreError 必须是 Exception，但不得是 ValueError。", "custom error is not ValueError"),
        ],
    },
    {
        "id": "eq-quiet-01",
        "category": "equivalence-side-effect",
        "difficulty": "simple",
        "allowed_path": "src/heartbeat.py",
        "facts": [
            ("record(at) 保持单参数公开签名。", "signature == ['at']"),
            ("record(7) 返回 {'at': 7, 'kind': 'heartbeat'}。", "canonical return object"),
            ("调用 record 时不得向 stdout 或 stderr 输出任何内容。", "no stdout/stderr output"),
            ("每次调用返回一个新 dict。", "returns a dict"),
        ],
    },
    {
        "id": "eq-money-01",
        "category": "equivalence-format",
        "difficulty": "moderate",
        "allowed_path": "src/money.py",
        "facts": [
            ("format_amount(cents) 保持单参数公开签名。", "signature == ['cents']"),
            ("cents 是非负 int，表示美分数。", "nonnegative integer cents"),
            ("format_amount(5) 返回 '$0.05'。", "five cents formats as $0.05"),
            ("format_amount(123456) 返回 '$1,234.56'。", "123456 cents formats as $1,234.56"),
            ("返回值必须是 str。", "return type is str"),
        ],
    },
    {
        "id": "eq-month-01",
        "category": "equivalence-mapping",
        "difficulty": "moderate",
        "allowed_path": "src/months.py",
        "facts": [
            ("month_name(number) 保持单参数公开签名。", "signature == ['number']"),
            ("month_name(1) 返回 'January'。", "1 maps to January"),
            ("month_name(12) 返回 'December'。", "12 maps to December"),
            ("number 为 0 或 13 时抛出 InvalidMonthError。", "out-of-range month raises InvalidMonthError"),
        ],
    },
    {
        "id": "eq-fallback-01",
        "category": "equivalence-control-flow",
        "difficulty": "moderate",
        "allowed_path": "src/fallback.py",
        "facts": [
            ("first_value(primary, secondary) 保持二参数公开签名。", "signature == ['primary', 'secondary']"),
            ("primary 必须恰好调用一次。", "primary called exactly once"),
            ("primary 返回非 None 时立即返回该值，并不得调用 secondary。", "non-None primary short-circuits"),
            ("primary 返回 None 时恰好调用 secondary 一次，并返回 secondary 的值。", "None primary calls secondary once"),
            ("primary 和 secondary 都返回 None 时返回 None。", "all-None returns None"),
        ],
    },
    {
        "id": "eq-clamp-01",
        "category": "equivalence-boundary",
        "difficulty": "simple",
        "allowed_path": "src/clamp.py",
        "facts": [
            ("clamp(value, low, high) 保持三参数公开签名。", "signature == ['value', 'low', 'high']"),
            ("输入保证 low <= high。", "low is not greater than high"),
            ("value 小于 low 时返回 low。", "below-bound returns low"),
            ("value 大于 high 时返回 high。", "above-bound returns high"),
            ("value 位于闭区间 [low, high] 内时原值返回。", "inside-bound returns value"),
        ],
    },
    {
        "id": "eq-window-01",
        "category": "equivalence-collection",
        "difficulty": "moderate",
        "allowed_path": "src/window.py",
        "facts": [
            ("window(values, start, stop) 保持三参数公开签名。", "signature == ['values', 'start', 'stop']"),
            ("start 是包含端点，stop 是不包含端点。", "inclusive start, exclusive stop"),
            ("越界部分按空序列处理，不得引发 IndexError。", "out-of-range positions are truncated"),
            ("返回结果必须是 list。", "return type is list"),
            ("不得原地修改传入的 values。", "input sequence remains unchanged"),
        ],
    },
    {
        "id": "eq-retry-01",
        "category": "equivalence-control-flow",
        "difficulty": "hard",
        "allowed_path": "src/bounded_retry.py",
        "facts": [
            ("retry(call, attempts) 保持二参数公开签名。", "signature == ['call', 'attempts']"),
            ("最多调用 call() attempts 次。", "call count is bounded by attempts"),
            ("成功时立即返回结果并停止调用。", "success short-circuits"),
            ("只重试 KeyError；其他异常必须立即原样抛出。", "non-KeyError propagates immediately"),
            ("达到上限后重新抛出最后一个 KeyError。", "last KeyError propagates after exhaustion"),
        ],
    },
]


def fact_lines(task):
    return [f"[{task['id']}/F{i:02d}] {text}" for i, (text, _) in enumerate(task["facts"], 1)]


def render(task, variant):
    lines = fact_lines(task)
    scope = f"[{task['id']}/S1] 只允许修改 {task['allowed_path']}；其他所有工作区文件必须保持不变。"
    evaluation = (
        f"[{task['id']}/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，"
        "不要声称自己运行了测试。"
    )
    if variant == "baseline":
        return "\n".join([
            "请按下方事实完成任务。",
            "必要事实：",
            *lines,
            "修改范围：",
            scope,
            "评估方式：",
            evaluation,
        ])
    if variant == "minimal":
        return "\n".join([
            "完成任务。",
            "事实：",
            *lines,
            "范围：",
            scope,
            "评估：",
            evaluation,
        ])
    if variant == "full":
        return "\n".join([
            "# 任务",
            "目标：满足全部原子事实。",
            "## 原子事实",
            *lines,
            "## 范围",
            scope,
            "## 评估",
            evaluation,
        ])
    raise ValueError(variant)


def build_rows():
    rows = []
    for task in TASKS:
        facts = [
            {
                "id": f"{task['id']}/F{i:02d}",
                "text": text,
                "hardness": "required",
                "counted": True,
                "oracle_assertion": oracle,
            }
            for i, (text, oracle) in enumerate(task["facts"], 1)
        ]
        scope = f"[{task['id']}/S1] 只允许修改 {task['allowed_path']}；其他所有工作区文件必须保持不变。"
        evaluation = (
            f"[{task['id']}/V1] 评估器会在收到完整文件内容后运行测试；本轮没有文件或终端工具，"
            "不要声称自己运行了测试。"
        )
        rows.append({
            "id": task["id"],
            "category": task["category"],
            "difficulty": task["difficulty"],
            "fixture": "synthetic-python-equivalence-v0.1",
            "schema_version": "information-equivalent-task-v0.1",
            "baseline": render(task, "baseline"),
            "minimal": render(task, "minimal"),
            "full": render(task, "full"),
            "atomic_facts": facts,
            "scope_facts": [{
                "id": f"{task['id']}/S1",
                "text": scope,
                "hardness": "required",
                "counted": True,
                "oracle_assertion": "unrequested files outside allowed_paths fail scorer",
            }],
            "evaluation_facts": [{
                "id": f"{task['id']}/V1",
                "text": evaluation,
                "hardness": "required",
                "counted": False,
                "oracle_assertion": "no-tool evaluation disclosure; not a hidden oracle assertion",
            }],
            "allowed_paths": [task["allowed_path"]],
            "forbidden_paths": [],
            "test_command": "python -m unittest discover -s tests",
            "oracle": f"{task['id']}_oracle",
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "tasks/manifest-information-equivalent-v0.1.jsonl")
    args = parser.parse_args()
    rows = build_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"tasks": len(rows), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
