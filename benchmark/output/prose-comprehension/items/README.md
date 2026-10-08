# Item Set v0.1

This first Output Track item set contains 10 short technical explanations.

Each item includes:

- one source fact sheet;
- Natural Chinese;
- Light ACL;
- Full ACL;
- two objectively scorable questions.

Domains include reverse proxies, transactions, caching, authentication, data pipelines, message queues, indexes, retries, API compatibility, and concurrency.

## Important limitation

The current validator checks structure and completeness. It does not prove semantic information equivalence between variants.

Before human-subject use, each item needs independent review against its fact sheet.

## Run validation

```bash
python benchmark/output/prose-comprehension/validate_items.py   benchmark/output/prose-comprehension/items/items-v0.1.jsonl
```
