# Benchmark Harness Self-Test

The benchmark scorer is tested against two deterministic controls:

1. **No-op control** — performs no code changes. It must fail every hidden behavioral oracle.
2. **Reference control** — applies known-correct minimal implementations. It must pass every task.

These controls do not validate ACL-ZH. They validate the benchmark harness itself.

The GitHub Actions workflow is:

`.github/workflows/benchmark-selftest.yml`

A benchmark result should not be trusted if this workflow is failing.
