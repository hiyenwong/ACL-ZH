#!/usr/bin/env python3
"""Deterministic reference implementation used only to self-test the benchmark scorer."""
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: reference_agent.py <prompt_file>")

prompt = Path(sys.argv[1]).read_text(encoding="utf-8")

if "get_user" in prompt and ("空格" in prompt or "首尾" in prompt):
    Path("src/user_service.py").write_text(
        "def get_user(user_id):\n    return {'id': user_id, 'name': '  Alice  '.strip()}\n",
        encoding="utf-8",
    )
elif "ConfigLoader.load" in prompt or "加载配置" in prompt:
    Path("src/config.py").write_text("""def parse_config(raw):
    out = dict(raw)
    if isinstance(out.get('debug'), str):
        v = out['debug'].lower()
        if v == 'true':
            out['debug'] = True
        elif v == 'false':
            out['debug'] = False
    return out

class ConfigLoader:
    def load(self, raw):
        return parse_config(raw)
""", encoding="utf-8")
elif "parse_bool" in prompt or "bool parser" in prompt:
    Path("src/parser.py").write_text("""def parse_bool(value):
    if isinstance(value, str):
        v = value.lower()
        if v == 'true':
            return True
        if v == 'false':
            return False
    return bool(value)
""", encoding="utf-8")
elif "缓存" in prompt or "cache" in prompt:
    Path("src/cache_service.py").write_text("""class CacheService:
    def __init__(self, cache, query):
        self.cache = cache
        self.query = query
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return self.query(key)
""", encoding="utf-8")
elif "normalize_name" in prompt:
    Path("src/names.py").write_text(
        "def normalize_name(value):\n    return ' '.join(value.split())\n",
        encoding="utf-8",
    )
elif "JSON" in prompt or "dumps" in prompt:
    Path("src/serializer.py").write_text(
        "import json\n\ndef dumps(value):\n    return json.dumps(value, sort_keys=True, separators=(',', ':'))\n",
        encoding="utf-8",
    )
elif "fallback" in prompt or "备用查询" in prompt or "兜底" in prompt:
    Path("src/resolver.py").write_text(
        "def resolve(key, primary, fallback):\n    value = primary(key)\n    return fallback(key) if value is None else value\n",
        encoding="utf-8",
    )
elif "safe_divide" in prompt or "除零" in prompt:
    Path("src/safe_math.py").write_text(
        "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None\n",
        encoding="utf-8",
    )
elif "format_name" in prompt or "uppercase" in prompt:
    Path("src/formatter.py").write_text(
        "def format_name(value, uppercase=False):\n    value = value.strip()\n    return value.upper() if uppercase else value\n",
        encoding="utf-8",
    )
elif "feature" in prompt or "enabled" in prompt or "transform" in prompt:
    Path("src/feature_gate.py").write_text(
        "def process(payload, enabled, transform):\n    if not enabled:\n        return payload\n    return transform(payload)\n",
        encoding="utf-8",
    )
elif "parse_timeout" in prompt or "timeout" in prompt:
    Path("src/settings.py").write_text(
        "def parse_timeout(value):\n    return int(value)\n",
        encoding="utf-8",
    )
    Path("src/client.py").write_text(
        "from .settings import parse_timeout\n\ndef get_timeout(config):\n    return parse_timeout(config.get('timeout', 30))\n",
        encoding="utf-8",
    )
elif "DEFAULT_REGION" in prompt or "默认区域" in prompt:
    Path("src/registry.py").write_text(
        "DEFAULT_REGION = 'us'\n\ndef endpoint(config):\n    region = config.get('region', DEFAULT_REGION)\n    return f'https://{region}.example.test'\n",
        encoding="utf-8",
    )
else:
    raise SystemExit("unknown self-test prompt")
