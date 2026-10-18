# Edit-Content Response Contract v0.1

Contract version: `edit-content-contract-v0.1`
Status: **frozen** (parser frozen since before the first scored run;
semantics pinned 2026-10-19 by the P2-01 fence-semantics decision)
Track: `local-lm-studio-edit-content` (diagnostic; never merged with
strict unified-diff counts)

## The contract

A compliant response consists of one or more FILE blocks and nothing
else:

```text
<<<FILE:path/to/file>>>
<complete final file content>
<<<END>>>
```

Requirements:

1. at least one well-formed FILE block;
2. no residual text outside blocks;
3. every block path is inside the task's `allowed_paths`;
4. no duplicate file path across blocks;
5. no empty file path;
6. no Markdown fence line anywhere in block content (see below);
7. no post-processing may be needed to satisfy any of the above.

## Fence semantics (P2-01 decision, preregistered)

**Decision: contract v0.1 prohibits every fence-looking content line.**
A line whose left-trimmed text starts with ` ``` ` or `~~~` anywhere in
a block's content is a contract violation, regardless of whether it
"wraps" the content or appears inside it.

### Why the strict rule

- The prompt contract text says "Do not wrap file content in Markdown
  fences". The scorer deliberately operationalizes this as the stricter
  total prohibition. This is a known wording gap, recorded here rather
  than silently harmonized.
- "Wrapper" vs "literal content" cannot be distinguished without
  inferring model intent; any such inference reintroduces the post-hoc
  leniency confound the parser freeze exists to prevent (see the 1.5B
  post-hoc audit, `benchmark/results/local-qwen25-coder-15b-semantic-v0.1/POSTHOC.md`).
- The strict rule is total, deterministic, and explainable: content is
  written to disk verbatim, so every emitted line is a file line.
- No current task family targets a file whose legitimate content
  contains fence lines (all targets are Python/source files), so the
  strict rule has zero false positives on the existing benchmark.

### Examples

Prohibited (each yields `markdown_fence_in_content:<path>`):

````text
<<<FILE:src/x.py>>>
```python
import json
...
```
<<<END>>>
````

````text
<<<FILE:src/x.py>>>
~~~
import json
...
~~~
<<<END>>>
````

````text
<<<FILE:src/x.py>>>
DOC = """
```
"""
<<<END>>>
````

The third shape is a fence line inside a string literal: still a v0.1
violation, by design.

Compliant:

````text
<<<FILE:src/x.py>>>
# Usage: `dumps(x)` — inline backticks are not fence lines
TICKS = "``"        # two backticks do not open a fence
def dumps(value): ...
<<<END>>>
````

### Known limitation and escape hatch

A future task family whose target file legitimately contains fence
lines (e.g. a Markdown document with embedded code examples) cannot be
expressed under contract v0.1. Supporting it requires:

1. a new contract version (e.g. `edit-content-contract-v0.2`) with
   explicit fence/escaping semantics, decided before any inference;
2. a versioned scorer implementing it, with dedicated tests;
3. v0.1 results preserved as-is — never silently reclassified.

## Version labeling of results

Every edit-content aggregate carries `contract_version` and a
provenance block (`scorer_sha256`, `parser_sha256`, …). All published
edit-content results to date (2026-10-14 runs) are contract v0.1.

## Frozen components

- `edit_content_parser.py` — block extraction (frozen; do not extend).
- The prompt contract text in `export_edit_content_prompts.py`
  (frozen together with the parser).
- Fence/duplicate/empty-path/residual detection lives in
  `score_edit_content_run.py` and may only be changed under the
  versioning rule above.
