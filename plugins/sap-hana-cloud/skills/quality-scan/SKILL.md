---
name: quality-scan
description: Run a lightweight quality scan of one HANA table.
---

Sequence:
1. Inspect schema with `hana_describe_table` or `hana_explain_table`.
2. Run a tiny row preview.
3. Use `hana_execute_query` to calculate row count and a few targeted quality checks: null counts, duplicate key checks, and suspicious value ranges.
4. Summarize quality signals, likely keys, and whether the table is feature-ready.
Guardrails:
- Keep checks lightweight and explicit.
- Prefer a few strong checks over a huge generic profile.
