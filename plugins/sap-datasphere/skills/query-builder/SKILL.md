---
name: query-builder
description: Guide the user from a business question to a working relational or analytical query. Use when the user wants to query data but is unsure which asset, columns, or filters to use.
---

Sequence:
1. Clarify the business question if needed. Identify the key entity (e.g. orders, customers, invoices, cost centres).
2. Run `datasphere_search_assets` with the entity name to find candidate assets.
3. Pick the best candidate. Run `datasphere_get_asset_metadata` to confirm it is queryable.
4. Run `datasphere_list_columns` to identify the relevant columns for the user's question.
   - Select columns: what the user wants to see
   - Filter columns: what the user wants to restrict by
   - Measure columns: what the user wants to aggregate
5. Run a small `datasphere_query_relational` with a sensible select and filter. Use top=10.
6. Review the result. If the asset supports analytical queries, try `datasphere_query_analytical` with a simple aggregation.
7. Present the final working query parameters the user can reuse, including:
   - space_id
   - asset_name
   - select columns
   - filter expression (if any)
   - recommended query type (relational or analytical)

Guardrails:
- Always preview before querying to confirm the asset has data.
- Use top=10 on first attempts. Do not fetch large result sets without user confirmation.
- If the relational query returns unexpected results, check schema and column types before adjusting.
