---
name: index-review
description: Inspect table indexes and comment on likely query performance implications.
---

Sequence:
1. Run `hana_list_indexes` for the table.
2. Run `hana_describe_index` for the important indexes.
3. Compare indexed columns to the user’s likely joins and filters.
4. Explain whether the current index layout matches the planned query pattern.
Guardrails:
- Present this as a metadata-based performance review, not a guaranteed optimizer verdict.
