---
name: data-quality-scan
description: Run a lightweight data-quality scan on one asset using preview, schema, and profiling. Use when the user asks whether a dataset looks usable.
---
<!-- File: plugins/sap-datasphere/skills/data-quality-scan/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Use `datasphere_describe_asset_schema`.
2. Preview a small row sample.
3. Choose one date-like column and one amount-like column when possible.
4. Profile those columns.
5. Report red flags: nulls, outliers, suspicious cardinality, inconsistent samples.

Keep the scan lightweight and read-only.
