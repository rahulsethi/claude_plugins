# Rahul Sethi's Claude Code Plugin Marketplace

Enterprise SAP plugins for [Claude Code](https://claude.ai/code), built and maintained by **Rahul Sethi**.

This marketplace connects Claude Code to SAP enterprise data platforms through the Model Context Protocol (MCP). Each plugin wraps a published MCP backend with skills, subagents, and guardrails designed for production data work. Plugins do not reimplement backend logic — they orchestrate it.

**Marketplace identifier:** `sethir-marketplace`

---

## Licensing and Enterprise Use

These plugins are licensed under the **[Elastic License 2.0 (ELv2)](LICENSE)**.

**Free for:**
- Individual developers using the plugins with their own HANA or Datasphere instances
- Enterprises deploying internally across their own employees and contractors
- Modification for internal use — no restrictions, no payment required

**Requires a commercial license for:**
- Providing these plugins as a hosted or managed service to third parties
- Embedding in a SaaS product or commercial platform sold to customers
- OEM redistribution or white-labeling

**Commercial licenses are available** — see [COMMERCIAL_LICENSE_AGREEMENT.md](COMMERCIAL_LICENSE_AGREEMENT.md) for terms and tiers, or contact [rahulsethi@github](https://github.com/rahulsethi) to discuss.

**Contributing?** Sign the [Contributor License Agreement](CONTRIBUTOR_LICENSE_AGREEMENT.md) before submitting a PR.

See [NOTICE](NOTICE) for full attribution requirements and third-party acknowledgements.

---

## Plugins

| Plugin | Version | Status | What it connects to |
|--------|---------|--------|---------------------|
| [sap-datasphere](#sap-datasphere) | `1.0.0-beta.2` | Beta | SAP Datasphere tenant via `sap-datasphere-mcp` |
| [sap-hana-cloud](#sap-hana-cloud) | `0.2.0-alpha.1` | Alpha | SAP HANA / HANA Cloud via [`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server) |

---

## Quick install

**Add this marketplace:**

```
/plugin marketplace add rahulsethi/claude_plugins
```

**Install a plugin:**

```
/plugin install sap-datasphere@sethir-marketplace
```
```
/plugin install sap-hana-cloud@sethir-marketplace
```

**Reload:**

```
/reload-plugins
```

Claude Code will prompt you for connection credentials on first use. Credentials are stored securely in the plugin's `userConfig` — never in plain text files or shell environment variables.

Full installation guides: [docs/sap-datasphere.md](docs/sap-datasphere.md) · [docs/sap-hana-cloud.md](docs/sap-hana-cloud.md)

---

## SAP Datasphere

**`sap-datasphere`** · `1.0.0-beta.2` · MIT · [Full guide →](docs/sap-datasphere.md)

A thin Claude Code wrapper around the [SAP Datasphere MCP server](https://github.com/rahulsethi/SAPDatasphereMCP). Gives Claude structured, read-only access to your Datasphere tenant — spaces, assets, columns, KPIs, lineage, and data quality — without requiring SQL knowledge or Datasphere UI navigation.

**This plugin is read-only throughout. No writes, no admin actions.**

### Prerequisites

1. Claude Code installed and updated
2. `mcp-sap-datasphere-server` package installed: `pip install mcp-sap-datasphere-server`
3. SAP Datasphere OAuth client (client ID + secret from BTP Cockpit)

### Install

```
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

### Skills (20)

**Orientation and discovery**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:tenant-recon` | Run diagnostics, list spaces, summarise a promising space |
| `/sap-datasphere:space-recon` | Summarise a single space and suggest starting assets |
| `/sap-datasphere:orientation-path` | Fastest path from zero context to a viable first query |
| `/sap-datasphere:cross-space-search` | Search a business concept across every space in the tenant |

**Asset exploration**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:asset-search` | Search for assets by business concept within a space |
| `/sap-datasphere:asset-explorer` | Inspect one asset end-to-end — metadata, columns, schema, preview |
| `/sap-datasphere:asset-card` | Produce a concise semantic summary card for an asset |
| `/sap-datasphere:compare-assets` | Compare two assets for structural similarity and join potential |
| `/sap-datasphere:schema-diff` | Side-by-side column schema comparison with join key analysis |

**Querying and analysis**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:query-builder` | Guide from business question to working relational or analytical query |
| `/sap-datasphere:analytical-check` | Verify analytical query support and run a sample |
| `/sap-datasphere:kpi-finder` | Identify candidate KPI and measure columns in a space |

**Data quality and governance**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:data-quality-scan` | Lightweight quality scan via preview, schema, and profiling |
| `/sap-datasphere:column-investigator` | Profile key columns for nulls, cardinality, and outliers |
| `/sap-datasphere:full-space-audit` | Comprehensive health and readiness audit of all assets |

**Advanced**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:join-hypothesis` | Find shared columns across assets and suggest likely joins |
| `/sap-datasphere:lineage-explorer` | Trace how a key column flows across assets in a space |

**Utilities**

| Command | What it does |
|---------|-------------|
| `/sap-datasphere:mock-mode-demo` | Safe demo flow using mock mode — no live tenant required |
| `/sap-datasphere:plugin-doctor` | Diagnose MCP setup and connectivity problems |
| `/sap-datasphere:release-smoke-test` | Manual smoke-test sequence for release validation |

### Agents (5)

| Agent | Model | Role |
|-------|-------|------|
| `datasphere-analyst` | Sonnet | Main analysis specialist — orientation through query |
| `datasphere-researcher` | Haiku | Lightweight discovery — shortlist spaces and assets |
| `datasphere-quality-reviewer` | Sonnet | Read-only quality and profiling reviewer |
| `datasphere-query-assistant` | Sonnet | Interactive guide from business question to executable query |
| `datasphere-data-steward` | Sonnet | Data governance and trust assessment |

### First commands

```
/sap-datasphere:tenant-recon
/sap-datasphere:orientation-path
/sap-datasphere:query-builder
```

---

## SAP HANA Cloud

**`sap-hana-cloud`** · `0.3.0-alpha.1` · MIT · [Full guide →](docs/sap-hana-cloud.md)

A thin Claude Code wrapper around [`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server) by [@HatriGt](https://github.com/HatriGt). Gives Claude structured access to SAP HANA and HANA Cloud databases — schema discovery, reviewed SQL writes, an end-to-end ML feature engineering workflow using Python `hana_ml` and PAL, and a full **ontology and knowledge graph pipeline** with SPARQL 1.1 compatibility.

The `hana-mcp-server` backend is pulled automatically via `npx` — no separate install step.

### What makes this different from sap-datasphere

| | sap-datasphere | sap-hana-cloud |
|-|---------------|----------------|
| Platform | SAP Datasphere (BW/DWC layer) | SAP HANA / HANA Cloud (SQL layer) |
| Access model | Read-only | Read + reviewed writes |
| Backend | Python MCP server | Node.js MCP server (npx) |
| ML support | None | Full hana_ml / PAL feature pipeline |
| Knowledge graph / SPARQL | None | Full KG pipeline + SPARQL 1.1 compatible triple store |
| Write guard | Not applicable | PreToolUse hook on every SQL call |

### Prerequisites

1. Claude Code installed and updated
2. Node.js 18 or later (for `npx hana-mcp-server`)
3. Network access to your HANA or HANA Cloud SQL endpoint
4. A technical HANA database user
5. Optional: Python + `hana-ml` for ML workflow generation
6. Optional: HANA Graph Engine provisioned for SPARQL endpoint (SQL-on-TRIPLES fallback requires no extra setup)

### Install

```
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
```

### Write guard

The plugin ships a `PreToolUse` hook that inspects every `hana_execute_query` call.

**Always blocked (regardless of `write_mode`):** `DROP`, `TRUNCATE`, `SHUTDOWN`, `ALTER SYSTEM`, `DELETE` without `WHERE`, multi-statement SQL.

**Controlled by `write_mode` config:**

| Setting | Behaviour |
|---------|-----------|
| `deny` | All non-`SELECT` SQL blocked |
| `ask` *(recommended)* | Claude pauses and shows you the SQL before executing any write |
| `allow` | Writes proceed automatically; always-blocked list still applies |

### Skills (44)

**Setup and discovery**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:connection-doctor` | Diagnose and verify HANA connection |
| `/sap-hana-cloud:plugin-doctor` | Verify hook, work schema, and MCP tool availability |
| `/sap-hana-cloud:landscape-recon` | List schemas, orient Claude to your HANA landscape |
| `/sap-hana-cloud:schema-recon` | Summarise one schema, highlight promising tables |
| `/sap-hana-cloud:table-explorer` | Inspect one table — columns, indexes, sample rows |
| `/sap-hana-cloud:semantics-bootstrap` | Create or extend a semantics JSON overlay file |

**Querying and analysis**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:query-builder` | Guide from business question to working HANA SQL |
| `/sap-hana-cloud:sql-preview-runner` | Run arbitrary SQL conservatively with previews |
| `/sap-hana-cloud:join-hypothesis` | Find likely join keys between two HANA tables |
| `/sap-hana-cloud:schema-diff` | Compare column schemas of two tables side by side |
| `/sap-hana-cloud:column-investigator` | Profile a column for meaning, nulls, and cardinality |
| `/sap-hana-cloud:quality-scan` | Lightweight quality scan of one HANA table |
| `/sap-hana-cloud:index-review` | Inspect table indexes and performance implications |

**Ontology and knowledge graph**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:relationship-discoverer` | Find FK constraints and naming-pattern relationships across all tables in a schema |
| `/sap-hana-cloud:entity-classifier` | Classify tables as FACT, DIMENSION, MASTER, REFERENCE, STAGING, or ANALYTICAL |
| `/sap-hana-cloud:ontology-planner` | Produce a Turtle (.ttl) ontology and JSON-LD context from schema discovery results |
| `/sap-hana-cloud:knowledge-graph-builder` | Materialize VERTICES + EDGES (property graph) and TRIPLES (RDF/SPARQL) tables in the work schema |
| `/sap-hana-cloud:column-cross-mapper` | Find all tables sharing a column name — reveals hub entities and implicit join paths |

**Schema discovery and lineage**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:view-explorer` | Discover and inspect SQL views and Calculation Views via SYS catalog |
| `/sap-hana-cloud:procedure-catalog` | List stored procedures and functions; identifies PAL algorithms automatically |
| `/sap-hana-cloud:lineage-graph` | Trace 3-level upstream/downstream object dependencies; outputs Mermaid flowchart |

**Extended profiling and cataloging**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:full-schema-profiler` | Multi-table catalog profiler — row counts, date ranges, null rates, cardinality across a whole schema |
| `/sap-hana-cloud:temporal-coverage-scan` | Analyze date columns across tables for freshness, history depth, and time-series alignment |
| `/sap-hana-cloud:distribution-analyzer` | Value distribution and suspicious-null detection for categorical/code columns |

**Reviewed writes**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:work-schema-bootstrap` | Plan or create a dedicated work schema |
| `/sap-hana-cloud:write-safety-primer` | Confirm the write guard is active; explains the workflow |
| `/sap-hana-cloud:write-plan-review` | Turn a requested change into a reviewed execution plan |
| `/sap-hana-cloud:reviewed-write-executor` | Execute reviewed DDL/DML through the guarded SQL tool |
| `/sap-hana-cloud:merge-upsert-planner` | Design a `MERGE` or `UPSERT` workflow |

**BI design**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:star-schema-designer` | Identify fact/dimension tables, validate join integrity, produce a star schema with SQL template |
| `/sap-hana-cloud:kpi-mapper` | Map plain-language business KPIs to validated SQL expressions |
| `/sap-hana-cloud:data-freshness-dashboard` | Summarise data freshness and load activity across key business tables |

**Curated dataset and modeling design**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:curated-dataset-recon` | Shortlist curated tables for a business question |
| `/sap-hana-cloud:score-date-design` | Define grain, score date, prediction horizon, leakage boundaries |
| `/sap-hana-cloud:training-split-planner` | Design time-aware train/validation/test splits |

**Feature engineering and PAL / hana_ml**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:feature-set-planner` | Design a leakage-aware ML feature set |
| `/sap-hana-cloud:feature-table-materializer` | Convert a feature plan into a materialized HANA table |
| `/sap-hana-cloud:pal-preflight` | End-to-end readiness check before any PAL or hana_ml work |
| `/sap-hana-cloud:pal-role-checker` | Audit PAL database roles and privileges for the current user |
| `/sap-hana-cloud:pal-sql-starter` | Generate a PAL SQL starter template |
| `/sap-hana-cloud:pal-python-starter` | Generate a Python `hana_ml` starter script |
| `/sap-hana-cloud:hana-ml-feature-flow` | Orchestrate the full source-to-Python feature pipeline |
| `/sap-hana-cloud:feature-output-audit` | Audit a materialized feature table for modeling readiness |

**Utilities**

| Command | What it does |
|---------|-------------|
| `/sap-hana-cloud:release-smoke-test` | Full 6-stage manual smoke-test sequence |

### Agents (13)

| Agent | Model | Role |
|-------|-------|------|
| `hana-analyst` | Sonnet | Main analysis specialist — schema, tables, query design |
| `hana-researcher` | Haiku | Lightweight schema and table shortlisting |
| `hana-curated-dataset-scout` | Haiku | Fast scout for curated and consumption-ready datasets |
| `hana-quality-reviewer` | Sonnet | Read-only reviewer — keys, nulls, duplicates, leakage risk |
| `hana-sql-engineer` | Sonnet | SQL design and query repair specialist |
| `hana-write-operator` | Sonnet | Reviewed DDL/DML specialist (CTAS, INSERT, MERGE) |
| `hana-feature-engineer` | Sonnet | Leakage-aware feature engineering and grain design |
| `hana-ml-engineer` | Sonnet | Bridges HANA metadata with Python `hana_ml` workflows |
| `hana-pal-operator` | Sonnet | PAL-oriented SQL planning and readiness checks |
| `hana-platform-advisor` | Sonnet | Architecture advisor — HANA Cloud, CAP, Fiori, BTP |
| `hana-ontologist` | Sonnet | Ontology and knowledge graph pipeline — relationship discovery through SPARQL triple store materialization |
| `hana-data-cataloger` | Sonnet | Comprehensive data catalog builder — profiles all tables, assesses quality and freshness |
| `hana-bi-architect` | Sonnet | BI layer design — star schema, KPI mapping, dimension/fact identification |

### Knowledge graph quick start

```
/sap-hana-cloud:relationship-discoverer   # map FK constraints and inferred joins
/sap-hana-cloud:entity-classifier         # classify tables as FACT/DIMENSION/MASTER/...
/sap-hana-cloud:ontology-planner          # produce OWL Turtle + JSON-LD ontology
/sap-hana-cloud:knowledge-graph-builder   # materialize VERTICES, EDGES, TRIPLES in work schema
```

Or run the full pipeline in one go:

```
@hana-ontologist Build a knowledge graph for the SALES schema
```

### First commands

```
/sap-hana-cloud:connection-doctor
/sap-hana-cloud:landscape-recon
/sap-hana-cloud:write-safety-primer
```

**Backend MCP server:** [`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server) by [@HatriGt](https://github.com/HatriGt) · MIT License

---

## Repository structure

```
claude_plugins/
├── .claude-plugin/
│   └── marketplace.json          marketplace manifest
├── plugins/
│   ├── sap-datasphere/           SAP Datasphere plugin (20 skills, 5 agents)
│   └── sap-hana-cloud/           SAP HANA Cloud plugin (44 skills, 13 agents)
├── docs/
│   ├── installation.md           install methods overview
│   ├── sap-datasphere.md         full SAP Datasphere installation and reference guide
│   ├── sap-hana-cloud.md         full SAP HANA Cloud installation and reference guide
│   └── contributing.md           contributing guide
├── .claude/
│   ├── skills/                   developer skills (/release, /validate-plugin)
│   ├── agents/                   developer agent (release-reviewer)
│   └── hooks/                    repo-level hooks (version-check, mcp-guard)
├── .mcp.json                     dev-only local MCP server
├── CLAUDE.md                     repo working rules for Claude Code sessions
└── smoke_test.py                 mock-mode smoke test
```

---

## License

This marketplace and all plugins are licensed under the **[Elastic License 2.0](LICENSE)**.

**What this means:**
- Free to use internally — individuals and enterprises can use these plugins in production without restriction
- Attribution required — you must retain copyright notices in any copy or fork
- No managed service — you may not provide these skills/agents as a hosted service to third parties without a commercial license
- No resale — you may not sublicense or resell the code

For use cases not covered by ELv2 (SaaS embedding, OEM distribution, white-labeling), contact [rahulsethi@github](https://github.com/rahulsethi) for a commercial license.

See also: [NOTICE](NOTICE) for attribution requirements and third-party acknowledgements.

> The backend MCP servers that these plugins call at runtime ([`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server), [`mcp-sap-datasphere-server`](https://github.com/rahulsethi/SAPDatasphereMCP)) are independent projects licensed under MIT. They are fetched at runtime and are not covered by this license.

## Author

[Rahul Sethi](https://github.com/rahulsethi)
