# Agent execution harness

This directory will hold executable A/B runs for Claude Code and Codex.

## Codex

OpenAI documents `codex exec` as the non-interactive automation path. A run must use the same model, reasoning effort, sandbox permissions, fixture commit, and timeout for baseline and ACL-ZH variants.

## Claude Code

Use Claude Code's non-interactive/print mode when available in the installed CLI. Record the exact CLI version and command in every result.

## Required controls

- Fresh checkout/worktree per run.
- Same starting commit.
- Same dependency cache state.
- Network either enabled for all runs or disabled for all runs.
- No ACL-ZH adapter loaded in the baseline arm.
- ACL-ZH adapter loaded only in the treatment arm when testing adapter effects.
- At least 5 repetitions per task/variant for stochastic models.
- Randomized order.
- Store raw stdout/stderr, git diff, command log, exit status, and test results.

Do not aggregate results across different model versions.
