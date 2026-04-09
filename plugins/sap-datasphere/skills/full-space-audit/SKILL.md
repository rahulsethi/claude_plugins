---
name: full-space-audit
description: Run a comprehensive health and readiness audit of all assets in a space. Use when the user wants an overview of what data is available, how queryable it is, and where quality gaps exist.
---

Sequence:
1. Run `datasphere_summarize_space` for the target space to get a high-level picture.
2. Run `datasphere_list_assets` to get the full asset list with types.
3. For each asset (up to 8), run `datasphere_get_asset_metadata` to check:
   - Relational query support
   - Analytical query support
   - Presence of a description (governance signal)
4. For the top 3 assets by analytical readiness, run `datasphere_describe_asset_schema`.
5. Compile a space health report:

   **Inventory**
   - Total assets by type (VIEW, TABLE, ANALYTIC MODEL, etc.)
   - Count with relational query support
   - Count with analytical query support

   **Governance gaps**
   - Assets with no description
   - Assets with empty or minimal schemas

   **Readiness rating**
   - High: has description + analytical support + non-empty schema
   - Medium: queryable but missing description or limited schema
   - Low: no query support or empty schema

6. Flag the top 2–3 most analytics-ready assets as recommended starting points.
7. Flag any assets with no query support as potential data engineering gaps.

Guardrails:
- Cap at 8 assets for metadata inspection to keep the audit lightweight.
- Prefer breadth over depth — do not deep-profile columns in this skill.
- If the space has more than 8 assets, sort by type and prioritise VIEW and ANALYTIC MODEL types.
