---
name: column-investigator
description: Profile one important column for meaning, quality, and modeling usefulness.
---

Sequence:
1. Use `hana_describe_table` or `hana_explain_table` to understand the column definition.
2. Run a small aggregation query with `hana_execute_query` to check nulls, distinct count, top values, min, and max as relevant.
3. Explain whether the column behaves like a key, label, category, date, or measure.
4. Flag anomalies such as heavy nulls, low cardinality surprises, or impossible values.
