---
name: lineage-explorer
description: Trace how a key column or business concept flows across assets in a space. Use when the user wants to understand data lineage or find all assets that share a common key or identifier.
---

Sequence:
1. Identify the key column or business term from the user's question (e.g. ORDER_ID, CUSTOMER_ID, MATERIAL_NUMBER).
2. Run `datasphere_find_assets_with_column` to find all assets in the space that carry that column.
3. For each matching asset (up to 4), run `datasphere_get_asset_metadata` to understand its type and query support.
4. If two or more strong candidates exist, run `datasphere_compare_assets_basic` on the pair most likely to be related (e.g. a fact table and a lookup table).
5. Sketch the likely data flow:
   - Source or staging asset (raw data, TABLE type)
   - Transformation or view asset (VIEW type, derived columns)
   - Consumption asset (analytical or reporting layer)
6. Note any gaps where lineage cannot be confirmed from metadata alone and suggest what additional inspection would resolve the uncertainty.

Guardrails:
- Do not claim confirmed lineage unless metadata strongly supports it.
- If `find_assets_with_column` returns no results, try `datasphere_find_assets_by_column` as a fallback.
- Keep the focus on the key column the user cares about, not every shared column.
