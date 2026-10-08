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
else:
    raise SystemExit("unknown self-test prompt")
