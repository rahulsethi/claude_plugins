---
name: schema-diff
description: Compare the schema of two tables side by side.
---

Sequence:
1. Run `hana_describe_table` for both sides.
2. Highlight exact column matches, name-only matches, type mismatches, and likely renamed fields.
3. Flag likely join keys and likely measures.
4. Summarize what the tables appear to represent and how interchangeable they are.
Return a crisp comparison instead of dumping both schemas verbatim.
