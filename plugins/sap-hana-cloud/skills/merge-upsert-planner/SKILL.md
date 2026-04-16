---
name: merge-upsert-planner
description: Design a HANA MERGE or UPSERT workflow for a feature or staging table.
---

Sequence:
1. Identify the source dataset and target table.
2. Confirm the business key and update columns.
3. Draft a `MERGE` or `UPSERT` statement.
4. Draft prechecks for duplicate source keys and target collisions.
5. Route the final statement through `reviewed-write-executor`.
Guardrails:
- Do not guess business keys.
- Call out what happens on matched and unmatched rows.
