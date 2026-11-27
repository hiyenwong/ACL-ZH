#!/usr/bin/env python3
"""Probe whether hidden-reasoning suppression actually works on an LM Studio endpoint.

This is a mechanism probe, not a benchmark run. It sends the same prompt under
several "do not think" conditions and records exactly how many completion
tokens were spent on hidden reasoning versus visible content.

Output: <workdir>/probe-results.json and <workdir>/probe-summary.md
"""
import argparse
import hashlib
import json
import platform
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROMPTS = {
    "trivial": "Reply with exactly one word, nothing else: OK",
    "arithmetic": "Compute 17*23. Reply with only the resulting integer, no explanation.",
    "edit": (
        "Rewrite this Python so it prints 6. Reply with the complete file only:\n"
        "print(2+3)\n"
    ),
}

# condition -> payload patch applied on top of the base payload
CONDITIONS = [
    ("baseline_no_effort", {}),
    ("effort_none", {"reasoning_effort": "none"}),
    ("effort_minimal", {"reasoning_effort": "minimal"}),
    ("effort_low", {"reasoning_effort": "low"}),
    ("template_enable_thinking_false", {"chat_template_kwargs": {"enable_thinking": False}}),
    ("no_think_suffix", {"_prompt_suffix": " /no_think"}),
]


def http_json(url, payload=None, timeout=600):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def reasoning_tokens(usage):
    if not isinstance(usage, dict):
        return None
    details = usage.get("completion_tokens_details") or {}
    for key in ("reasoning_tokens", "reasoning_token_count"):
        if isinstance(details.get(key), int):
            return details[key]
        if isinstance(usage.get(key), int):
            return usage[key]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=20261011)
    ap.add_argument("--only-prompt", default=None)
    args = ap.parse_args()

    root = Path(args.workdir)
    root.mkdir(parents=True, exist_ok=True)

    models = http_json(args.base_url.rstrip("/") + "/models", timeout=60)
    ids = [m.get("id") for m in models.get("data", [])]
    if args.model not in ids:
        raise SystemExit(f"Model {args.model!r} not loaded; available: {ids}")

    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    prompts = {k: v for k, v in PROMPTS.items() if args.only_prompt in (None, k)}

    rows = []
    for prompt_name, prompt in prompts.items():
        for cond_name, patch in CONDITIONS:
            patch = dict(patch)
            suffix = patch.pop("_prompt_suffix", "")
            payload = {
                "model": args.model,
                "messages": [{"role": "user", "content": prompt + suffix}],
                "temperature": args.temperature,
                "seed": args.seed,
                "max_tokens": args.max_tokens,
                "stream": False,
            }
            payload.update(patch)
            started = time.time()
            row = {
                "prompt": prompt_name,
                "condition": cond_name,
                "payload_extra": patch or None,
                "prompt_suffix": suffix or None,
                "requested_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            try:
                result = http_json(endpoint, payload=payload, timeout=args.timeout)
                choice = (result.get("choices") or [{}])[0]
                message = choice.get("message") or {}
                content = message.get("content") or ""
                reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
                usage = result.get("usage") or {}
                row.update({
                    "ok": True,
                    "finish_reason": choice.get("finish_reason"),
                    "visible_chars": len(content),
                    "visible_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
                    "reasoning_chars": len(reasoning) if isinstance(reasoning, str) else 0,
                    "reasoning_field_present": "reasoning_content" in message or "reasoning" in message,
                    "completion_tokens": usage.get("completion_tokens"),
                    "reasoning_tokens": reasoning_tokens(usage),
                    "usage_keys": sorted(usage.keys()),
                    "response_id": result.get("id"),
                    "visible_preview": content[:160],
                })
            except Exception as exc:  # noqa: BLE001 - probe records failures verbatim
                row.update({"ok": False, "error": str(exc)[:800]})
            row["elapsed_seconds"] = round(time.time() - started, 2)
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
            (root / "probe-results.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    meta = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "reasoning-suppression-mechanism-probe",
        "model": args.model,
        "base_url": args.base_url,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "seed": args.seed,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version,
        "prompts": prompts,
        "conditions": [c[0] for c in CONDITIONS],
        "rows": rows,
    }
    (root / "probe-metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = ["# Reasoning-suppression probe", "", f"Model: `{args.model}`, max_tokens {args.max_tokens}", "",
             "| prompt | condition | ok | finish | visible chars | reasoning tokens | reasoning field | completion tokens |",
             "|---|---|---:|---|---:|---:|---|---:|"]
    for r in rows:
        lines.append(
            "| {p} | {c} | {ok} | {f} | {v} | {rt} | {rf} | {ct} |".format(
                p=r["prompt"], c=r["condition"], ok="yes" if r.get("ok") else "NO",
                f=r.get("finish_reason"), v=r.get("visible_chars"),
                rt=r.get("reasoning_tokens"), rf=r.get("reasoning_field_present"),
                ct=r.get("completion_tokens"),
            )
        )
    (root / "probe-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
