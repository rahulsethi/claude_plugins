---
name: schema-diff
description: Compare the column schemas of two assets side by side to find structural differences, shared keys, and compatibility. Use when the user wants to understand whether two assets cover the same entity or can be joined.
---

Sequence:
1. Confirm the two asset names and space IDs (they may be in the same space or different spaces).
2. Run `datasphere_list_columns` for both assets.
3. Run `datasphere_describe_asset_schema` for both assets to get type and example value information.
4. If both assets are in the same space, run `datasphere_compare_assets_basic`.
5. Compute the diff:
   - Columns present in both assets (potential join keys or shared dimensions)
   - Columns only in asset A
   - Columns only in asset B
   - Type mismatches on columns with the same name
6. Report:
   - Most plausible join key(s) based on name and type similarity
   - Likely grain difference (if any)
   - Whether the assets appear to be the same entity at different levels, related fact/dimension pair, or unrelated

Guardrails:
- Do not claim join correctness unless shared column names and types align strongly.
- Note when assets are in different spaces — cross-space joins may not be directly supported.
- Flag any column that appears in both assets but with mismatched types as a data integration risk.
