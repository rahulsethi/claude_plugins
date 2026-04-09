# New Skills and Agents Run: sap-datasphere Plugin
**Date:** 2026-04-08
**Version bump:** 1.0.0-beta.1 → 1.0.0-beta.2
**Scope:** Add 6 new end-user plugin skills and 2 new agents to `plugins/sap-datasphere/`.

---

## Summary

| Item | Type | Location | Status |
|------|------|----------|--------|
| `cross-space-search` | Skill | `plugins/sap-datasphere/skills/cross-space-search/SKILL.md` | ADDED |
| `lineage-explorer` | Skill | `plugins/sap-datasphere/skills/lineage-explorer/SKILL.md` | ADDED |
| `query-builder` | Skill | `plugins/sap-datasphere/skills/query-builder/SKILL.md` | ADDED |
| `schema-diff` | Skill | `plugins/sap-datasphere/skills/schema-diff/SKILL.md` | ADDED |
| `kpi-finder` | Skill | `plugins/sap-datasphere/skills/kpi-finder/SKILL.md` | ADDED |
| `full-space-audit` | Skill | `plugins/sap-datasphere/skills/full-space-audit/SKILL.md` | ADDED |
| `datasphere-query-assistant` | Agent | `plugins/sap-datasphere/agents/datasphere-query-assistant.md` | ADDED |
| `datasphere-data-steward` | Agent | `plugins/sap-datasphere/agents/datasphere-data-steward.md` | ADDED |
| `plugin.json` | Version bump | `.claude-plugin/plugin.json` | UPDATED |
| `marketplace.json` | Version bump | `.claude-plugin/marketplace.json` | UPDATED |
| `README.md` | Skills/agents list, grouped categories | `plugins/sap-datasphere/README.md` | UPDATED |
| `CHANGELOG.md` | New entry for 1.0.0-beta.2 | `plugins/sap-datasphere/CHANGELOG.md` | UPDATED |

---

## New Skills (6)

### `cross-space-search`
**Trigger:** User doesn't know which space holds the data they need.
**Tools used:** `datasphere_list_spaces`, `datasphere_search_assets`
**What it does:** Iterates across all spaces (up to 5), collates and ranks results by relevance, returns top 5 candidates across the tenant with a recommended starting point.
**Gap filled:** Existing `asset-search` is single-space only; no prior skill searched the full tenant.

---

### `lineage-explorer`
**Trigger:** User wants to understand data lineage or find all assets sharing a common key.
**Tools used:** `datasphere_find_assets_with_column`, `datasphere_find_assets_by_column`, `datasphere_get_asset_metadata`, `datasphere_compare_assets_basic`
**What it does:** Finds all assets carrying a named column, inspects their metadata, compares likely related pairs, sketches source→transformation→consumption flow.
**Gap filled:** No existing skill traced column-level lineage across assets.

---

### `query-builder`
**Trigger:** User wants to query data but is unsure which asset, columns, or filters to use.
**Tools used:** `datasphere_search_assets`, `datasphere_get_asset_metadata`, `datasphere_list_columns`, `datasphere_preview_asset`, `datasphere_query_relational`, `datasphere_query_analytical`
**What it does:** Full guided flow from business question → asset → columns → working query. Presents reusable query parameters at the end.
**Gap filled:** No existing skill built a query interactively from a business question.

---

### `schema-diff`
**Trigger:** User wants to understand if two assets cover the same entity or can be joined.
**Tools used:** `datasphere_list_columns` (×2), `datasphere_describe_asset_schema` (×2), `datasphere_compare_assets_basic`
**What it does:** Side-by-side column comparison, identifies shared columns, columns unique to each asset, type mismatches, and suggests plausible join keys.
**Gap filled:** `compare-assets` does a basic comparison; `schema-diff` goes deeper with type analysis and explicit diff output.

---

### `kpi-finder`
**Trigger:** User asks what metrics, amounts, or measures are available in a space.
**Tools used:** `datasphere_list_assets`, `datasphere_list_columns`, `datasphere_profile_column`
**What it does:** Scans asset column names for measure-like patterns (Amount, Value, Revenue, Cost, etc.), profiles top candidates to confirm numeric and non-trivial distribution, returns a ranked KPI table.
**Gap filled:** No existing skill identified measure columns systematically across a space.

---

### `full-space-audit`
**Trigger:** User wants a comprehensive view of data availability, quality, and analytical readiness in a space.
**Tools used:** `datasphere_summarize_space`, `datasphere_list_assets`, `datasphere_get_asset_metadata`, `datasphere_describe_asset_schema`
**What it does:** Inventories all assets by type, checks query support and governance fields, rates each asset HIGH/MEDIUM/LOW readiness, flags governance gaps (missing descriptions), recommends best starting assets.
**Gap filled:** `space-recon` is lightweight; `full-space-audit` does a full governance + readiness sweep across all assets.

---

## New Agents (2)

### `datasphere-query-assistant`
**Model:** sonnet
**Disallowed tools:** none (can query)
**Role:** Interactive guide from business question to executable query.
**When to use:** User wants a query result but doesn't know where to start. Goes from "I need sales data" to a working `query_relational` or `query_analytical` call with reusable parameters.
**Distinguishes from `datasphere-analyst`:** The analyst does broad exploration; this agent is focused specifically on building and refining queries.

---

### `datasphere-data-steward`
**Model:** sonnet
**Disallowed tools:** Write, Edit (read-only by design)
**Role:** Data governance and trust assessment.
**When to use:** Before using a dataset in reporting or analysis. Rates datasets LOW/MEDIUM/HIGH trust based on schema, preview, and column profiles. Flags governance gaps (missing descriptions, unnamed columns, null-heavy columns).
**Distinguishes from `datasphere-quality-reviewer`:** The quality reviewer is a background checker; the steward is user-facing, explains findings in business terms, and explicitly rates trust level.

---

## Updated Files

### `plugins/sap-datasphere/README.md`
- Skills list expanded from 14 to 20
- Skills grouped into workflow categories: Orientation, Asset Exploration, Querying and Analysis, Data Quality and Governance, Advanced, Utilities
- Agents list expanded from 3 to 5
- Recommended first tests updated

### `plugins/sap-datasphere/CHANGELOG.md`
- New entry: `[1.0.0-beta.2] — 2026-04-08` with all 6 skills and 2 agents listed

### `plugins/sap-datasphere/.claude-plugin/plugin.json`
- `version`: `1.0.0-beta.1` → `1.0.0-beta.2`

### `.claude-plugin/marketplace.json`
- `plugins[0].version`: `1.0.0-beta.1` → `1.0.0-beta.2`

---

## Tool Coverage After This Release

All new skills use only confirmed v0.3.0 tools. No new tool dependencies introduced.

| New Skill | Tools Used |
|-----------|-----------|
| cross-space-search | list_spaces, search_assets |
| lineage-explorer | find_assets_with_column, find_assets_by_column, get_asset_metadata, compare_assets_basic |
| query-builder | search_assets, get_asset_metadata, list_columns, preview_asset, query_relational, query_analytical |
| schema-diff | list_columns, describe_asset_schema, compare_assets_basic |
| kpi-finder | list_assets, list_columns, profile_column |
| full-space-audit | summarize_space, list_assets, get_asset_metadata, describe_asset_schema |

---

## Plugin Skill Count After This Release

| Category | Count |
|----------|-------|
| Skills | 20 (was 14) |
| Agents | 5 (was 3) |
| MCP tools available (v0.3.0) | 22 |

---

## Next Steps

Run validation to confirm the new skills are correctly structured:
```
/validate-plugin
```

Then test manually in a `--plugin-dir` session:
```
claude --plugin-dir ./plugins/sap-datasphere

/sap-datasphere:cross-space-search
/sap-datasphere:query-builder
/sap-datasphere:full-space-audit
```
