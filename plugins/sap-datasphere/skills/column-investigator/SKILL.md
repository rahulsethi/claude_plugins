---
name: column-investigator
description: Profile key columns to identify IDs, dimensions, measures, null issues, and outliers. Use when the user asks about field meaning or data quality.
---
<!-- File: plugins/sap-datasphere/skills/column-investigator/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Identify one ID-like column and one measure-like or category-like column.
2. Use `datasphere_profile_column` on each.
3. If available, use `datasphere_summarize_column_profile` for a cleaner summary.
4. Explain role hints, null patterns, distinctness, and anomalies.

Return a crisp field-by-field interpretation rather than raw stats only.
