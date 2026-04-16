---
name: schema-recon
description: Summarize one schema and highlight promising tables. Use when the user knows the schema and wants a fast inventory.
---

Sequence:
1. Run `hana_list_tables` for the target schema.
2. Pick up to 3 promising tables by name.
3. Run `hana_describe_table` on those tables.
4. If semantics are configured, prefer `hana_explain_table` for the top candidate.
Return a schema note with: table count seen, top candidates, likely grain, likely measures, and the best next table to explore.
