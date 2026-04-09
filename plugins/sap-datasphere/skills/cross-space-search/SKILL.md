---
name: cross-space-search
description: Search for a business concept across every space in the tenant, not just one. Use when the user does not know which space holds the data they need.
---

Sequence:
1. Run `datasphere_list_spaces` to retrieve all visible spaces.
2. For each space (up to 5), run `datasphere_search_assets` with the user's business terms.
3. Collate all results. Deduplicate by asset ID.
4. Rank by relevance: prefer assets with descriptions, prefer VIEW types, prefer names that closely match the query.
5. Return the top 5 candidates across all spaces with: space, asset name, type, and description.
6. Recommend the strongest match as the starting point and suggest running `asset-explorer` on it.

Guardrails:
- If more than 5 spaces exist, prioritise the ones whose names most closely match the user's business domain.
- Do not claim a match is correct — present evidence and let the user confirm.
- If no matches are found across any space, suggest broadening the search terms.
