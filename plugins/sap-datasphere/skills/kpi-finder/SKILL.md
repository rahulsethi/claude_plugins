---
name: kpi-finder
description: Identify candidate KPI and measure columns in a space. Use when the user asks what metrics, amounts, quantities, or numerical measures are available for analysis.
---

Sequence:
1. Run `datasphere_list_assets` for the target space.
2. Filter for assets most likely to contain facts or measures: prefer VIEW and TABLE types over lookup-style names.
3. For the top 3 candidate assets, run `datasphere_list_columns`.
4. Identify columns whose names suggest measures using these patterns:
   - Amount, Value, Quantity, Count, Revenue, Cost, Price, Rate, Score, Balance, Total, Sum, Margin, Weight
5. For the strongest 2–3 measure candidates across all inspected assets, run `datasphere_profile_column` to confirm they are numeric and non-trivially distributed (not all nulls, not constant).
6. Return a ranked table:

   | Asset | Column | Likely KPI Role | Null % | Min | Max | Mean |
   |-------|--------|-----------------|--------|-----|-----|------|

7. Recommend the best 1–2 KPIs for immediate use in an analytical or relational query.

Guardrails:
- Only claim a column is a KPI if it is numeric and has meaningful variance in the profile.
- If no obvious measure columns exist, report the finding and suggest inspecting a different space or asset type.
- Keep profiling lightweight: use default sample sizes.
