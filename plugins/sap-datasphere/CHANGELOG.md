<!-- File: plugins/sap-datasphere/CHANGELOG.md -->
<!-- Version: v2 -->

# Changelog

## [1.0.0-beta.2] — 2026-04-08
### Added
- `cross-space-search` skill: search a business concept across all tenant spaces, not just one.
- `lineage-explorer` skill: trace how a key column flows across assets via `find_assets_with_column` and `compare_assets_basic`.
- `query-builder` skill: guided path from a business question to a working relational or analytical query.
- `schema-diff` skill: side-by-side column schema comparison between two assets with join key analysis.
- `kpi-finder` skill: identify candidate KPI and measure columns in a space using column profiling.
- `full-space-audit` skill: comprehensive health and readiness audit of all assets in a space.
- `datasphere-query-assistant` agent: interactive query guide (sonnet); goes from vague business question to executable query.
- `datasphere-data-steward` agent: read-only data governance and trust assessment agent (sonnet); rates datasets LOW/MEDIUM/HIGH trust.

### Changed
- README restructured: skills grouped by workflow category (orientation, exploration, querying, quality, advanced, utilities).
- Recommended first tests updated to reflect new cross-space and query-builder workflows.

## [1.0.0-beta.1]
### Added
- Initial Claude Code wrapper plugin scaffold for SAP Datasphere MCP.
- Plugin `userConfig` for Datasphere connection values.
- Thin `.mcp.json` launcher for `sap-datasphere-mcp`.
- Workflow-oriented Datasphere skills (14 skills).
- Datasphere-focused subagents (3 agents).
