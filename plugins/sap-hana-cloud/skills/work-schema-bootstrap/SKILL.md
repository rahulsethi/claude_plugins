---
name: work-schema-bootstrap
description: Plan or create a dedicated work schema for reviewed writes, feature tables, and PAL outputs.
---

Sequence:
1. Explain why a separate work schema is recommended.
2. Confirm the configured work schema `${user_config.work_schema}` or ask the user to choose one.
3. Draft SQL for schema creation, grants, and naming conventions.
4. If the user wants to execute it, route through `write-plan-review` and then `reviewed-write-executor`.
Guardrails:
- Never assume schema creation rights exist.
- Keep source curated schemas read-mostly.
