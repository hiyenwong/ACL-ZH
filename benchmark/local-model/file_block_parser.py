import re

BLOCK_RE = re.compile(r'<<<([^>\n]+)>>>\s*\n```(?:python)?\s*\n(.*?)```', re.S | re.I)

def extract_blocks(text):
    return [(path.strip(), content.rstrip() + '\n') for path, content in BLOCK_RE.findall(text)]
