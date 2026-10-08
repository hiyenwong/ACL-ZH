import json, re, statistics
from pathlib import Path

AMBIG = ["尽量","最好","适当","合理","看情况","必要时","简单","稍微","顺便","这里","这个","那个","它","上面","之前","原来的","没问题","处理一下","确认没问题"]
EXPLICIT = ["目标：","范围：","任务：","约束：","验证：","停止条件：","条件：","术语："]
ACTION = ["修改","运行","删除","创建","验证","报告","更新","检查","识别","重构","搜索","复用","添加","记录","返回","使用","保留","声明"]
FLOW = ["如果","否则","仅当","当"]
NORM = ["必须","不得","应该","可以"]

def score(text):
    return {
        "chars": len(text),
        "ambiguity_hits": sum(text.count(x) for x in AMBIG),
        "explicit_sections": sum(1 for x in EXPLICIT if x in text),
        "action_terms": sum(text.count(x) for x in ACTION),
        "flow_markers": sum(text.count(x) for x in FLOW),
        "normative_markers": sum(text.count(x) for x in NORM),
        "exact_identifier_refs": len(re.findall(r"(?:[\\w./-]+\\.(?:ts|js|py|yaml|yml|json|md)|\\w+\\.\\w+\\(\\)|ADR-\\d+|src/[\\w/*.-]+)", text)),
        "validation_evidence": int(("退出码" in text or "exit code" in text) and ("验证" in text or "测试" in text)),
    }

def ambiguity_index(m):
    return (
        2 * m["ambiguity_hits"]
        - 0.5 * m["explicit_sections"]
        - 0.5 * m["flow_markers"]
        - 0.5 * m["normative_markers"]
        - 0.5 * m["exact_identifier_refs"]
        - m["validation_evidence"]
    )

rows = []
path = Path(__file__).parent / "cases.jsonl"
for line in path.read_text(encoding="utf-8").splitlines():
    c = json.loads(line)
    b, a = score(c["baseline"]), score(c["acl"])
    b["ambiguity_index"] = ambiguity_index(b)
    a["ambiguity_index"] = ambiguity_index(a)
    rows.append({"id": c["id"], "category": c["category"], "baseline": b, "acl": a})

aggregate = {}
for variant in ["baseline", "acl"]:
    keys = rows[0][variant].keys()
    aggregate[variant] = {
        k: round(statistics.mean(r[variant][k] for r in rows), 3)
        for k in keys
    }

print(json.dumps({
    "n_cases": len(rows),
    "aggregate": aggregate,
    "cases": rows,
    "warning": "Static linguistic comparison only; this does not prove better downstream agent performance."
}, ensure_ascii=False, indent=2))
