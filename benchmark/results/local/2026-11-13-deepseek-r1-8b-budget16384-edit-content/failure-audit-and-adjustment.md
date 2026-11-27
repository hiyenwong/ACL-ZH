# Failure audit and prospective transport adjustment

Source run: ad7d19bf-24d4-4ce8-88cf-ab5644a022e2. No rescoring.

Observed output failures include residual explanations, Markdown fences in
file contents, and malformed opening markers such as <<<src/user_service.py>>>
instead of <<<FILE:src/user_service.py>>>. Some responses with malformed
markers contain plausible implementations, but they remain failures under
the frozen contract and have NOT been normalized or reclassified.

## dependency-mirror

| Variant | Semantic pass but contract fail | Semantic fail | Format violations (nonexclusive) |
|---|---:|---:|---|
| baseline | 1 | 3 | {'residual_text': 4} |
| minimal | 3 | 1 | {'residual_text': 3, 'no_file_blocks': 1} |
| full | 1 | 3 | {'residual_text': 2} |
## constraint

| Variant | Semantic pass but contract fail | Semantic fail | Format violations (nonexclusive) |
|---|---:|---:|---|
| baseline | 1 | 3 | {'markdown_fence_in_content': 2, 'residual_text': 3} |
| minimal | 3 | 3 | {'residual_text': 3, 'markdown_fence_in_content': 4} |
| full | 2 | 6 | {'residual_text': 3, 'no_file_blocks': 4} |

## Additional semantic and design limitations

The Full dependency response sorts JSON keys but omits compact separators;
this is a real semantic omission, not solely a serialization problem.
The Baseline parse_id implementation uses a signed-number regex that
interprets ID-42 as -42; this does not meet the intended identifier behavior.
A wrapper fix cannot guarantee correction of either failure.

Input fixture code is presented in Markdown fences by the old exporter;
output fence copying is a plausible mechanism, not a demonstrated cause.
The old prompt also requests tests in some task variants while providing
no terminal tools. A common no-tools clarification avoids implied tool use;
it cannot remove all task-information inequivalence.

Manual inspection of all 12 constraint prompt triples found non-equivalent
explicitness and hard/soft constraints: dependency Baseline says preferably
avoid dependencies while Minimal/Full prohibit them; Full schema explicitly
preserves 0/False/empty strings; Full token forbids encoding/case changes;
retry variants differ in explicit exception scope. This is not an independent
blinded equivalence audit. The next transport test leaves these exact
instructions unchanged to isolate a wrapper-level intervention, and cannot
support confirmatory causal claims about language structure alone.

## Adjustment

Create a child retaining the established 16384-token condition. Replace only
the shared exporter wrapper: fence-free source presentation, literal FILE:
prefix reminder, syntax-only example, no prose/fences reminder, no-tools
clarification. Preserve manifests, accepted response contract, parser and
oracle. Run 48 calls with the same task order and report primary and semantic
outcomes separately. Historical comparison remains exploratory; the bundled
wrapper intervention does not identify a single component's causal effect.

New protocol: benchmark/local-model/PREREG-TRANSPORT-V2.md.
Regression check exports both wrappers for every task/variant and verifies
identical metadata, unchanged instruction text and source contents.
