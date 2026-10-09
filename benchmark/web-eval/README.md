# Web-manual Input Track

This track is for experiments performed through free browser chat products when API access is unavailable.

It is not equivalent to Codex, Claude Code, or another coding agent with filesystem and terminal tools.

## Experimental unit

Each task bundle contains the ACL-ZH prompt variant, the relevant starting files, allowed/forbidden path metadata, and a strict response contract: return a unified diff only.

The browser model never receives hidden tests or hidden oracles.

## Suggested browser candidates

- Gemini web app with a fixed displayed model.
- Hugging Face Chat with a fixed named model.
- Qwen Chat or another browser-accessible named model.

Do not use an automatic router if the exact underlying model is unknown.

Record provider, exact displayed model name, date, reasoning/thinking setting, login requirement, and the raw first response.

## Export prompts

Run export_web_prompts.py with manifest.jsonl and one of baseline, minimal, or full. The output directory contains six Markdown prompt bundles plus metadata.

## Browser protocol

1. Start a fresh chat for every task and every variant.
2. Paste the entire generated Markdown prompt.
3. Do not send any follow-up clarification.
4. Save the first response exactly as returned.
5. If the model adds prose or Markdown fences around the diff, preserve them. The scorer must not silently clean the answer.

## Score

Run score_web_patch.py with the manifest, task id, variant, provider, exact model name, raw response file, and output JSONL.

The scorer uses the same fixture, visible tests, hidden oracle, forbidden-path detection, and unrequested-change detection as the CLI-agent benchmark.

## Evidence boundary

`web-manual` answers whether a browser chat model can produce a correct first-shot patch under different instruction styles.

It does not establish that ACL-ZH improves an autonomous coding agent with tools. Keep `web-manual` and `agent-cli` results separate.
