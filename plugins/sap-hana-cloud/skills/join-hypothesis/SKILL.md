---
name: join-hypothesis
description: Find likely join keys between two HANA tables and draft a first join query.
---

Sequence:
1. Run `hana_describe_table` on both tables.
2. Compare names, types, and likely business keys.
3. If needed, run tiny distinct or count previews with `hana_execute_query` to test key overlap.
4. Draft a small joined `SELECT` with `maxRows` 10.
5. Explain the most likely join type and why.
Guardrails:
- Call out grain mismatches explicitly.
- Avoid large exploratory joins before validating keys.
