---
name: table-explorer
description: Inspect one HANA table end to end. Use when the user wants to understand columns, meaning, and a tiny preview.
---

Sequence:
1. Run `hana_describe_table`.
2. Run `hana_explain_table` if semantics are available.
3. Identify likely keys, dates, measures, and status columns.
4. Run `hana_execute_query` with a tiny `SELECT *` preview and `maxRows` 10.
5. If the table is truncated, mention `snapshotId` and `hana_query_next_page` as needed.
Guardrails:
- Keep previews small.
- Explain column roles in plain English, not only raw metadata.
