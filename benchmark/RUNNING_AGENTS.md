# Running real agent benchmarks

This document describes how to run the ACL-ZH benchmark against real coding-agent CLIs.

## Supported execution paths

### OpenAI Codex

Codex supports non-interactive automation with `codex exec`. For evals, `--json` emits a JSONL event stream suitable for archiving and deterministic inspection.

Authentication in CI uses the repository secret:

`CODEX_ACCESS_TOKEN`

Official references:

- https://developers.openai.com/blog/eval-skills/
- https://developers.openai.com/zh-Hans/docs/enterprise/access-tokens
- https://developers.openai.com/blog/codex-as-a-platform/

### Claude Code

Claude Code supports non-interactive mode with `claude -p` / `--print`, JSON output, model selection, and turn limits.

Authentication in CI uses the repository secret:

`ANTHROPIC_API_KEY`

Official reference:

- https://docs.anthropic.com/en/docs/claude-code/cli-usage

## GitHub Actions

Use:

`Actions → Agent benchmark → Run workflow`

Choose:

- agent: `codex` or `claude`;
- exact model name or supported CLI alias;
- reasoning effort metadata;
- repetitions;
- timeout.

The workflow runs all three variants:

- Baseline;
- Minimal ACL;
- Full ACL.

Results are uploaded as a GitHub Actions artifact and are **not automatically committed** to the repository.

This is intentional. A result should be reviewed before it becomes a published benchmark result.

## Required controls

Do not compare runs if any of these differ without clearly stratifying the result:

- model/model version;
- CLI version;
- reasoning effort;
- task manifest commit;
- ACL-ZH specification commit;
- sandbox/permission policy;
- network policy.

## Security note

The benchmark uses ephemeral synthetic repositories. Real-agent jobs should only be run from trusted repository state because agent CLIs necessarily receive authentication credentials in CI.

Do not enable this workflow for untrusted pull-request code with write-capable secrets.

## Result promotion

After a run:

1. download the artifact;
2. inspect raw JSONL and traces;
3. verify environment metadata;
4. rerun suspicious failures;
5. commit accepted raw results under `benchmark/results/agent/`;
6. update `benchmark/results/README.md`;
7. only then update top-level README conclusions.
