# sap-hana-cloud Claude Code Plugin

**Version:** `0.3.0-alpha.1` · **44 skills · 13 agents**

This plugin is a **thin Claude Code wrapper** around the published **`hana-mcp-server`** package.

It does not reimplement the backend. Instead, it:
- starts `hana-mcp-server` through `npx`
- collects HANA connection and guardrail settings through Claude Code plugin `userConfig`
- adds HANA-focused discovery, query, write, ontology/knowledge graph, and `hana_ml` workflow skills
- adds reusable subagents for analysis, SQL design, reviewed writes, PAL / `hana_ml` planning, ontology building, data cataloging, and BI design
- ships a plugin hook that guards `hana_execute_query` so non-read-only SQL is reviewed before execution

## What this plugin is good for

- Exploring HANA Cloud schemas, tables, views, and stored procedures
- Understanding table meaning with optional semantics JSON
- Building cautious SQL step by step with previews before execution
- **Building OWL/RDF ontologies from HANA schema discovery results**
- **Materializing HANA-native knowledge graphs** with a SPARQL 1.1-compatible triple store (TRIPLES table) and property graph tables (VERTICES + EDGES) in a work schema
- Comprehensive multi-table data catalog profiling — row counts, date ranges, distributions, freshness
- Tracing object lineage using HANA's SYS dependency catalog
- Designing star and snowflake BI schemas from entity-classified tables
- Mapping business KPIs to validated HANA SQL expressions
- Materializing reviewed feature tables into a work schema for ML pipelines
- Planning PAL and `hana_ml` workflows for Python-first projects

## What this plugin is **not**

- **Not an ML runtime.** It plans feature tables and generates starter Python, but it does not train or run models.
- **Not a HANA admin tool.** It reads metadata and runs reviewed SQL. It cannot create users, configure tenants, or manage roles beyond what your technical user already has.
- **Not a PAL execution engine.** It generates PAL SQL and checks readiness; PAL algorithms run inside HANA.
- **Not a standalone SPARQL triple store.** The TRIPLES table lives in HANA — it requires a HANA database to host it.
- **Not a CAP or Fiori builder.**

## Prerequisites

1. Claude Code installed and updated.
2. Node.js 18 or later.
3. Reachability to your HANA or HANA Cloud SQL endpoint.
4. A technical HANA user with `SELECT` on target schemas, `CREATE TABLE`/`INSERT` on the work schema for writes, and `CATALOG READ` for SYS catalog queries (views, FKs, lineage, ontology discovery).
5. Optional: Python virtual environment with `hana-ml` installed.
6. Optional: HANA Graph Engine provisioned for SPARQL endpoint (SQL-on-TRIPLES requires no extra setup).

## Local development test

From the marketplace repo root:

```bash
claude --plugin-dir ./plugins/sap-hana-cloud
```

Then inside Claude Code:

```text
/reload-plugins
/help
/agents
```

## Install from your marketplace repo

```text
/plugin marketplace add ./
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
```

## Configuration collected by the plugin

- HANA host, port, user, password
- Default schema
- Connection type (`auto`, `single_container`, `mdc_system`, `mdc_tenant`)
- MDC instance number and tenant name if needed
- SSL, encrypt, and certificate validation flags
- Max result rows
- Optional semantics file path or URL
- Log level
- Write mode: `deny`, `ask`, or `allow`
- Work schema — for feature tables, KG tables, PAL outputs, and staging tables

## How write mode works

The HANA MCP backend allows arbitrary SQL through `hana_execute_query`. This plugin ships with a **PreToolUse hook** that inspects every SQL statement before it runs.

**Always blocked — no matter what write mode you set:**
- `DROP`, `TRUNCATE`, `SHUTDOWN`, `ALTER SYSTEM`
- `DELETE` without a `WHERE` clause
- Multi-statement SQL (more than one statement separated by `;`)

**Controlled by `write_mode`:**

| Setting | Behaviour |
|---------|-----------|
| `deny` | All non-read-only SQL is blocked. |
| `ask` *(recommended)* | Claude pauses and shows you the SQL before executing any write. |
| `allow` | Writes run without a confirmation prompt. The always-blocked list still applies. |

> **Note:** Knowledge graph builds (`knowledge-graph-builder`) use reviewed writes. Each CREATE TABLE and INSERT goes through the write guard. Set `write_mode = ask` to review each step.

## Knowledge graph and SPARQL

The plugin can build a HANA-native knowledge graph from any schema. Three tables are created in the work schema:

| Table | Purpose |
|-------|---------|
| `KG_<SCHEMA>_VERTICES` | Entity nodes — one row per table, with entity type, IRI, and row/column counts |
| `KG_<SCHEMA>_EDGES` | Relationship edges — FK (CONFIRMED) and naming-pattern (INFERRED) with confidence |
| `KG_<SCHEMA>_TRIPLES` | RDF triple store — SUBJECT, PREDICATE, OBJECT following W3C RDF model |

The TRIPLES table can be queried three ways:

1. **SQL on TRIPLES** — standard SQL joins, always available, no extra HANA setup
2. **HANA Graph Service REST** — SPARQL 1.1 POST to the Graph Engine REST endpoint (requires Graph Engine provisioned)
3. **HANA GRAPH WORKSPACE** — Cypher-like GRAPH queries after a DBA creates the workspace

Full SPARQL query examples and setup instructions are in [docs/sap-hana-cloud.md](../../docs/sap-hana-cloud.md#knowledge-graph-and-sparql).

**Full KG pipeline:**
```
/sap-hana-cloud:relationship-discoverer
/sap-hana-cloud:entity-classifier
/sap-hana-cloud:ontology-planner
/sap-hana-cloud:knowledge-graph-builder
```

Or via the agent:
```
@hana-ontologist Build a knowledge graph for the SALES schema
```

## Included skills

### Setup and discovery
- `connection-doctor`
- `plugin-doctor`
- `landscape-recon`
- `schema-recon`
- `table-explorer`
- `semantics-bootstrap`

### Querying and analysis
- `query-builder`
- `sql-preview-runner`
- `join-hypothesis`
- `schema-diff`
- `column-investigator`
- `quality-scan`
- `index-review`

### Ontology and knowledge graph
- `relationship-discoverer` — FK + naming-pattern edge discovery across a schema
- `entity-classifier` — FACT / DIMENSION / MASTER / REFERENCE / STAGING classification
- `ontology-planner` — Turtle (.ttl) OWL ontology + JSON-LD @context
- `knowledge-graph-builder` — VERTICES + EDGES + TRIPLES tables + SPARQL queries + GRAPH WORKSPACE DDL
- `column-cross-mapper` — shared column name ranking for hub key and implicit FK discovery

### Schema discovery and lineage
- `view-explorer` — SQL views and Calculation Views via SYS catalog
- `procedure-catalog` — stored procedures and functions; identifies PAL algorithms
- `lineage-graph` — 3-level upstream/downstream dependency tracing with Mermaid output

### Extended profiling and cataloging
- `full-schema-profiler` — multi-table row counts, date ranges, null rates, cardinality
- `temporal-coverage-scan` — freshness and historical depth analysis across all date columns
- `distribution-analyzer` — value distribution for categorical/code columns

### Reviewed writes
- `work-schema-bootstrap`
- `write-safety-primer`
- `write-plan-review`
- `reviewed-write-executor`
- `merge-upsert-planner`

### BI design
- `star-schema-designer` — fact/dimension identification + star schema SQL template
- `kpi-mapper` — plain-language KPI → validated SQL expression
- `data-freshness-dashboard` — load monitoring across key tables; optional monitoring VIEW

### Curated dataset and modeling design
- `curated-dataset-recon`
- `score-date-design`
- `training-split-planner`

### Feature engineering and PAL / `hana_ml`
- `feature-set-planner`
- `feature-table-materializer`
- `pal-preflight`
- `pal-role-checker`
- `pal-sql-starter`
- `pal-python-starter`
- `hana-ml-feature-flow`
- `feature-output-audit`

### Utilities
- `release-smoke-test`

## Included agents

- `hana-analyst` — main HANA discovery and SQL analyst
- `hana-researcher` — lightweight schema and table shortlisting (Haiku)
- `hana-curated-dataset-scout` — curated/consumption-ready dataset scout (Haiku)
- `hana-quality-reviewer` — data quality and profiling reviewer (read-only)
- `hana-sql-engineer` — query design and query repair specialist
- `hana-write-operator` — cautious reviewed write specialist
- `hana-feature-engineer` — feature-table design specialist
- `hana-ml-engineer` — `hana_ml` and PAL workflow planner
- `hana-pal-operator` — PAL SQL and readiness specialist
- `hana-platform-advisor` — CAP, Fiori, BTP, and architecture advisor (read-only)
- `hana-ontologist` — full ontology + knowledge graph pipeline; SPARQL-aware (max 30 turns)
- `hana-data-cataloger` — comprehensive data catalog builder for full schema assessment (read-only)
- `hana-bi-architect` — star schema, KPI mapping, and BI layer design advisor (read-only)

## Recommended first tests

```text
/sap-hana-cloud:connection-doctor
```
Checks that the MCP server can reach your HANA endpoint and that your credentials work.

```text
/sap-hana-cloud:landscape-recon
```
Lists the schemas Claude can see. Shows counts of tables and views per schema.

```text
/sap-hana-cloud:table-explorer
```
Browses one schema's tables — column names, types, row counts, and example values.

```text
/sap-hana-cloud:write-safety-primer
```
Explains the write guard and confirms it is active before you attempt any writes.

```text
/sap-hana-cloud:relationship-discoverer
```
Discovers FK constraints and naming-pattern relationships in a schema. First step for ontology work.

```text
/sap-hana-cloud:full-schema-profiler
```
Builds a catalog card for every table in a schema — great first pass for any new dataset.
