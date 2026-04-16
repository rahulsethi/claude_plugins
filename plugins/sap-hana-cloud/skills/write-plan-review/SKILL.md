---
name: write-plan-review
description: Turn a requested DDL or DML change into a reviewed execution plan.
---

Sequence:
1. Restate what will change: schema, objects, row scope, and expected result.
2. Separate the request into prechecks, the write statement, and postchecks.
3. Preview the source data or affected rows with `SELECT` queries first.
4. Draft the exact write SQL.
5. Draft rollback or cleanup SQL when possible.
6. Hand off to `reviewed-write-executor` only after the plan is explicit.
Guardrails:
- Prefer one statement at a time.
- Avoid hidden side effects.
