---
name: curated-dataset-recon
description: Shortlist curated HANA tables or views for a business question before detailed analysis.
---

Sequence:
1. Ask the user: business outcome, scoring entity (customer / order / machine / other), and whether a score date or target label column is already known.
2. Call `hana_list_schemas`. Skip system schemas (SYS, _SYS_*, HANA_XS_*, PUBLIC). Focus on schemas whose names suggest curated data: DATA_MART, CURATED, CONSUMPTION, CDW, BW, REPORTING, or domain names.
3. For each candidate schema call `hana_list_tables`. Look for curated signals in object names:
   - Suffixes: `_C`, `_VIEW`, `_FACT`, `_DIM`, `_CONSUMPTION`, `_ML`, `_SCORED`
   - Presence of obvious key columns, event date columns, and measure columns visible in the name
4. For the top 5 to 8 candidates call `hana_describe_table` to get columns and `hana_explain_table` for any semantic notes.
5. Rank the best 3 to 5 tables. For each state: why it looks curated, its likely grain (one row per what), its best candidate key column, its best candidate event date column, and whether it suits a label source, feature source, or both.
6. If semantics config is present (`${user_config.semantics_path}` or `${user_config.semantics_url}`), check it first — semantic annotations override name-based guessing.
7. Hand off to `feature-set-planner` with a plain-text shortlist: table name, schema, key column, event date column, suggested role.

Guardrails:
- Prefer views and semantics-annotated objects over raw landing tables.
- State explicitly when the shortlist is based only on naming conventions, not confirmed data quality.
- If no curated candidates are found, tell the user and ask them to provide table names directly.
