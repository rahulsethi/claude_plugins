---
name: asset-explorer
description: Inspect one asset end-to-end using metadata, columns, schema, and preview. Use when the user wants to understand a specific asset.
---
<!-- File: plugins/sap-datasphere/skills/asset-explorer/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Run `datasphere_get_asset_metadata`.
2. Run `datasphere_list_columns`.
3. Run `datasphere_describe_asset_schema`.
4. Run `datasphere_preview_asset`.
5. Summarize the asset in practical analyst language.

Focus on:
- what the asset likely represents
- key IDs, dimensions, and measures
- whether the sample looks trustworthy
- which follow-up query to run next
