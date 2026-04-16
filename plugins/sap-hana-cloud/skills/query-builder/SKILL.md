---
name: query-builder
description: Guide the user from a business question to a working HANA SQL preview.
---

Sequence:
1. Clarify the business question, grain, filters, and time window.
2. Use `hana_list_tables`, `hana_describe_table`, or `hana_explain_table` to find the best source table or tables.
3. Draft a small `SELECT` with explicit columns and `maxRows` 10.
4. Run `hana_execute_query` and inspect the result.
5. Refine joins, filters, and aggregations only after the preview looks right.
6. Return the final reviewed SQL plus any assumptions you made.
Guardrails:
- Prefer `SELECT` and `WITH` previews first.
- Do not jump straight to large scans or writes.
