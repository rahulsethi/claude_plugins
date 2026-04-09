---
name: analytical-check
description: Check whether an asset supports analytical queries and run a small analytical query if it does. Use when the user asks for analytical capability or summary slicing.
---
<!-- File: plugins/sap-datasphere/skills/analytical-check/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Use `datasphere_get_asset_metadata`.
2. Verify whether analytical queries are supported.
3. If yes, run a small `datasphere_query_analytical` with safe limits.
4. If no, say so clearly and suggest a relational fallback.

Always mention whether the result was analytical or relational.
