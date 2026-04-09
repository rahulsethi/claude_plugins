<!-- File: plugins/sap-datasphere/README.md -->
<!-- Version: v2 -->

# sap-datasphere Claude Code Plugin

This plugin is a **thin Claude Code wrapper** around the existing **SAP Datasphere MCP server**.

It does not reimplement the backend. Instead, it:

- starts the `sap-datasphere-mcp` CLI as a plugin MCP server
- collects tenant configuration through Claude Code plugin `userConfig`
- adds Datasphere-oriented skills
- adds reusable subagents for research, analysis, and data governance

## Prerequisites

1. Claude Code installed and updated.
2. The backend CLI available in your shell:

```bash
sap-datasphere-mcp
```

If not installed yet:

```bash
pip install mcp-sap-datasphere-server
```

or:

```bash
pipx install mcp-sap-datasphere-server
```

## Local development test

From the marketplace repo root:

```bash
claude --plugin-dir ./plugins/sap-datasphere
```

Then inside Claude Code:

```text
/reload-plugins
/help
/agents
```

## Install from a marketplace

```text
/plugin marketplace add <owner>/<repo>
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

## Configuration collected by the plugin

- tenant URL
- OAuth token URL
- client ID
- client secret
- verify TLS flag
- mock mode flag

These values are exported into the MCP process environment.

## Included skills

### Orientation and discovery
- `tenant-recon` — diagnose the tenant, list spaces, summarise one promising space
- `space-recon` — summarise a single space and suggest starting assets
- `orientation-path` — fastest path from zero context to a viable first query
- `cross-space-search` — search a business concept across every space in the tenant

### Asset exploration
- `asset-search` — search for assets by business concept within a space
- `asset-explorer` — inspect one asset end-to-end (metadata, columns, schema, preview)
- `asset-card` — produce a concise semantic summary card for an asset
- `compare-assets` — compare two assets for structural similarity and join potential
- `schema-diff` — side-by-side column schema comparison with join key analysis

### Querying and analysis
- `analytical-check` — verify analytical query support and run a sample analytical query
- `query-builder` — guide from a business question to a working relational or analytical query
- `kpi-finder` — identify candidate KPI and measure columns in a space

### Data quality and governance
- `data-quality-scan` — lightweight data quality scan using preview, schema, and profiling
- `column-investigator` — profile key columns for nulls, cardinality, and outliers
- `full-space-audit` — comprehensive health and readiness audit of all assets in a space

### Advanced
- `join-hypothesis` — find shared columns across assets and suggest likely joins
- `lineage-explorer` — trace how a key column flows across assets in a space

### Utilities
- `mock-mode-demo` — safe demo flow using DATASPHERE_MOCK_MODE
- `plugin-doctor` — diagnose MCP setup problems
- `release-smoke-test` — manual release smoke test sequence

## Included agents

- `datasphere-analyst` — main analysis specialist; guides from orientation to query (sonnet)
- `datasphere-researcher` — lightweight discovery agent for shortlisting spaces and assets (haiku)
- `datasphere-quality-reviewer` — read-only quality and profiling reviewer (sonnet)
- `datasphere-query-assistant` — interactive guide from business question to executable query (sonnet)
- `datasphere-data-steward` — data governance and trust assessment agent (sonnet)

## Recommended first tests

```text
/sap-datasphere:tenant-recon
/sap-datasphere:cross-space-search
/sap-datasphere:query-builder
```
