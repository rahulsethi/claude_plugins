---
name: sql-preview-runner
description: Run arbitrary SQL conservatively. Use when the user already has SQL and wants a safe preview-oriented execution flow.
---

Checklist:
1. Inspect whether the SQL is read-only (`SELECT` or `WITH`) or write-capable.
2. For read-only SQL, run `hana_execute_query` with explicit `maxRows`.
3. For non-read-only SQL, explain what the write guard hook will do based on write mode.
4. If a result is truncated, explain how to continue with `hana_query_next_page`.
5. Summarize returned rows, truncation, and the next adjustment.
Guardrails:
- Always mention when SQL is changing the database.
- Encourage `write-plan-review` before DDL or DML.
