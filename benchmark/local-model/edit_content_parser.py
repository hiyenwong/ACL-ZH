"""Frozen parser for the edit-content diagnostic track.

Preregistered contract (frozen before any scored run on this track):

    <<<FILE:path/to/file>>>
    <complete final file content>
    <<<END>>>

Do not extend this parser post-hoc. The 1.5B semantic audit
(benchmark/results/local-qwen25-coder-15b-semantic-v0.1/POSTHOC.md)
showed that introducing a lenient parser after inspecting model output
is a methodological confound. Models that emit fences or other shapes
fail format_compliant, and that failure is the measurement.
"""
import re

BLOCK_RE = re.compile(r'<<<FILE:([^>\n]+)>>>\s*\n(.*?)\n<<<END>>>', re.S)


def extract_file_blocks(text):
    """Return [(path, content)] in emission order. Content is verbatim."""
    return [(path.strip(), content) for path, content in BLOCK_RE.findall(text)]


def residual_text(text):
    """Text left over after removing all well-formed blocks."""
    return BLOCK_RE.sub('', text).strip()
