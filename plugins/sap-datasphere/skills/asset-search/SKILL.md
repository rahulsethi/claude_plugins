---
name: asset-search
description: Search across spaces for a business concept and shortlist the best candidate assets. Use when the user asks for employee, sales, finance, invoice, order, or similar data.
---
<!-- File: plugins/sap-datasphere/skills/asset-search/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Use `datasphere_search_assets` with the user’s business terms.
2. Shortlist the strongest matches.
3. For the best 1 to 3 results, call `datasphere_get_asset_metadata`.
4. Recommend the best starting asset and explain why.

Prefer assets that:
- have clear descriptions
- expose relational queries
- expose analytical queries when analysis is likely
