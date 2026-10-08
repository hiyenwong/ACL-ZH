# Information Equivalence Audit v0.1

Status: **FAIL — revision required before human study**

The first manual audit reviewed all 10 items against their source fact sheets.

## Findings

Four items contain material extra information in the Natural variant:

- cache-01
- index-01
- retry-01
- api-01
- lock-01

In addition, a systematic confound exists in Full ACL: semantic headings such as “风险”, “优化”, and “判断依据” sometimes closely match the question category. This can improve lookup performance independently of controlled-language clarity.

## Decision

Do not start a human study with items-v0.1.

Required remediation:

1. remove or add source facts so every arm is information-equivalent;
2. reduce category-label answer cues;
3. rerun manual equivalence review;
4. publish a new item-set version rather than silently overwriting the audit history.

Detailed machine-readable findings: `audit-v0.1.json`.
