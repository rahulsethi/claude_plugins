---
name: reviewed-write-executor
description: Execute reviewed DDL or DML through the guarded SQL tool.
---

Sequence:
1. Confirm the plan already exists. If not, call `write-plan-review` first.
2. Confirm the target schema and target objects. Prefer `${user_config.work_schema}` when appropriate.
3. Run the precheck `SELECT` queries first.
4. Run the reviewed DDL or DML with `hana_execute_query`.
5. Explain what the hook is expected to do based on write mode.
6. Run postcheck `SELECT` queries to verify the outcome.
Guardrails:
- Be explicit that this changes the database.
- Never hide the SQL from the user.
- Avoid destructive statements and mass deletes.
