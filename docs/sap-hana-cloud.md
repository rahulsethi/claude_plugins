# SAP HANA Cloud Plugin — Installation and Reference Guide

**Plugin:** `sap-hana-cloud` · **Version:** `0.2.0-alpha.1` · **Marketplace:** `sethir-marketplace`

This plugin is a thin Claude Code wrapper around [`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server), an open-source MCP server for SAP HANA and HANA Cloud maintained by [@HatriGt](https://github.com/HatriGt).

It gives Claude structured access to SAP HANA databases — schema and table discovery, cautious SQL execution, reviewed DDL/DML writes, a full ML feature engineering workflow using Python `hana_ml` and PAL, and a complete **ontology and knowledge graph pipeline** that materializes HANA-native SPARQL-queryable graph stores.

> **Backend MCP server credit:** This plugin depends on [`hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server) by [@HatriGt](https://github.com/HatriGt), licensed MIT. The plugin wraps and orchestrates it — it does not reimplement HANA connectivity.

---

## How it works

```
Claude Code ──► sap-hana-cloud plugin ──► hana-mcp-server (via npx) ──► HANA SQL endpoint
                (skills, agents, hook)     (Node.js MCP server)           (HANA JDBC)
```

The plugin starts `hana-mcp-server` via `npx -y hana-mcp-server` when Claude Code launches. The `npx` command pulls the latest published package from npm automatically — no separate install step required as long as Node.js 18+ is available.

A `PreToolUse` hook intercepts every `hana_execute_query` call before it reaches the database and either allows, asks for confirmation, or blocks the SQL based on its content and your `write_mode` setting.

---

## What this plugin does

- Connects to SAP HANA or HANA Cloud via the `hana-mcp-server` MCP backend
- Explores schemas, tables, columns, indexes, views, and stored procedures through natural language
- Builds and previews SQL queries step by step before execution
- Executes reviewed DDL and DML (CREATE, INSERT, MERGE, ALTER TABLE) through a write guard
- **Discovers foreign key constraints and naming-pattern relationships across your schemas**
- **Builds OWL/RDF ontologies from schema classification and relationship discovery results**
- **Materializes HANA-native knowledge graphs** — property graph tables (VERTICES + EDGES) for HANA GRAPH queries, and an RDF triple store (TRIPLES) for SPARQL 1.1 queries — all in the work schema
- Generates sample SPARQL queries and explains all three execution paths (SQL fallback, Graph Service REST, SPARQL_EXECUTE)
- Profiles schemas comprehensively — row counts, date ranges, value distributions, data freshness
- Traces object lineage using HANA's `SYS.OBJECT_DEPENDENCIES`
- Designs star and snowflake BI schemas from entity-classified tables
- Maps business KPIs to validated SQL expressions
- Plans and materializes ML feature tables with leakage-aware design
- Generates Python `hana_ml` starters and PAL SQL templates ready for your project code

## What this plugin does not do

- **Not an ML runtime.** It generates Python starters — it does not run `hana_ml` algorithms itself.
- **Not a HANA admin tool.** Cannot create users, configure tenants, or manage roles beyond your technical user's grants.
- **Not a PAL execution engine.** Generates PAL SQL and checks readiness; PAL algorithms run inside your HANA instance.
- **Not a standalone SPARQL triple store.** The TRIPLES table lives in HANA and requires a HANA database to host it.
- **Not a CAP or Fiori builder.**
- Does not reimplement `hana-mcp-server` — it wraps the published npm package.

---

## Prerequisites

### 1. Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

### 2. Node.js 18 or later

`hana-mcp-server` runs via `npx`. Node.js 18+ must be on your PATH:

```bash
node --version   # must be 18.x or higher
npx --version
```

On Windows, the recommended install is via [nodejs.org](https://nodejs.org) or `winget install OpenJS.NodeJS`.

### 3. HANA connectivity

- Network access from your workstation to the HANA or HANA Cloud SQL endpoint
- Port 443 (HANA Cloud) or 31015 / 31013 (on-premise HANA)
- A technical HANA database user with:
  - `SELECT` on the schemas you want Claude to explore
  - `CATALOG READ` system privilege for SYS catalog queries (views, procedures, FK constraints, lineage, knowledge graph discovery)
  - `CREATE TABLE`, `INSERT`, `MERGE` on the work schema if you want reviewed writes or knowledge graph materialization
  - PAL role grants if you plan to use PAL SQL execution (see [pal-role-checker](#pal-role-checker))

### 4. Optional — Python and hana-ml

Only needed if you want Claude to generate Python starters that you will run locally:

```bash
pip install hana-ml
```

The plugin generates the Python code — you run it in your own environment.

### 5. Optional — HANA Graph Engine (for SPARQL endpoint)

Required only for Option B SPARQL execution (HANA Graph Service REST API or `SPARQL_EXECUTE`). The knowledge graph triple store can always be queried via plain SQL (Option A) without the Graph Engine.

In SAP HANA Cloud, the Graph Engine is provisioned through the HANA Cloud Central. Contact your HANA Cloud administrator if the Graph Engine is not available. The plugin's SQL-on-TRIPLES query path works independently of Graph Engine provisioning.

---

## Installation methods

### Method 1 — From GitHub marketplace (recommended)

```
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
```

Claude Code will prompt you for connection credentials. See the [Configuration](#configuration) section.

### Method 2 — From local clone

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
```

Then inside Claude Code opened in the cloned directory:

```
/plugin marketplace add ./
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
```

### Method 3 — Direct plugin-dir (development or offline)

Load the plugin for a single session without marketplace installation. Useful for testing changes to the plugin itself:

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
```

Set environment variables, then launch:

```bash
export HANA_HOST='your-hana-host.hanacloud.ondemand.com'
export HANA_PORT='443'
export HANA_USER='CLAUDE_TECHNICAL_USER'
export HANA_PASSWORD='your$password'
export HANA_SCHEMA='YOUR_DEFAULT_SCHEMA'
export HANA_SSL='true'
export HANA_ENCRYPT='true'
export HANA_VALIDATE_CERT='true'

claude --plugin-dir ./plugins/sap-hana-cloud
```

### Method 4 — npx MCP server only (without the plugin wrapper)

If you want to add the raw `hana-mcp-server` directly to Claude Code without the plugin's skills and agents — for example, to use it alongside your own prompts — you can register it as a standalone MCP server:

```bash
claude mcp add sap-hana-cloud npx -y hana-mcp-server
```

Then set the required environment variables in your Claude Code MCP config. This gives you the raw HANA MCP tools (`hana_list_schemas`, `hana_describe_table`, `hana_execute_query`, etc.) without the plugin's skills, write guard, or agents.

To use the skills, knowledge graph pipeline, and write guard, use Method 1, 2, or 3 instead.

---

## Configuration

When installing through the marketplace, Claude Code prompts for these values. Credentials are stored in Claude's secure plugin config store — not written to disk.

| Field | Environment variable | Description | Sensitive |
|-------|---------------------|-------------|-----------|
| HANA Host | `HANA_HOST` | SQL endpoint hostname, e.g. `xxx.hanacloud.ondemand.com` | No |
| HANA Port | `HANA_PORT` | SQL port: `443` for HANA Cloud, `31015` for on-prem | No |
| HANA User | `HANA_USER` | Technical database user name | No |
| HANA Password | `HANA_PASSWORD` | Database user password | **Yes** |
| Default Schema | `HANA_SCHEMA` | Schema Claude uses when none is specified | No |
| Connection Type | `HANA_CONNECTION_TYPE` | `auto`, `single_container`, `mdc_system`, or `mdc_tenant` | No |
| Instance Number | `HANA_INSTANCE_NUMBER` | Two-digit instance number for MDC landscapes | No |
| Database Name | `HANA_DATABASE_NAME` | Tenant database name for MDC tenant connections | No |
| Use SSL | `HANA_SSL` | `true` (required for HANA Cloud) or `false` | No |
| Encrypt Connection | `HANA_ENCRYPT` | `true` or `false` | No |
| Validate Certificate | `HANA_VALIDATE_CERT` | `true` or `false`. Set `false` only for self-signed lab setups | No |
| Max Result Rows | `HANA_MAX_RESULT_ROWS` | Per-page cap on query results, e.g. `50` | No |
| Semantics File Path | `HANA_SEMANTICS_PATH` | Path to a local JSON file with table/column meanings | No |
| Semantics URL | `HANA_SEMANTICS_URL` | HTTPS URL for the same semantics JSON shape | No |
| Metadata Catalog Database | `HANA_METADATA_CATALOG_DATABASE` | MDC catalog database name for metadata tools | No |
| Log Level | `LOG_LEVEL` | `error`, `warn`, `info`, or `debug` | No |
| Write Mode | *(plugin config only)* | `deny`, `ask`, or `allow` — controls the write guard | No |
| Work Schema | *(plugin config only)* | Schema for feature tables, KG tables, PAL outputs, and staging tables | No |

**Update credentials at any time:**

```
/plugin config sap-hana-cloud
```

---

## Write guard

The plugin ships a `PreToolUse` hook (`hooks/hooks.json` + `scripts/hana_sql_guard.py`) that intercepts every `hana_execute_query` call before it executes.

### Always blocked — regardless of write_mode

These statements are hard-blocked with no confirmation prompt:

| Statement | Why |
|-----------|-----|
| `DROP TABLE / VIEW / SCHEMA` | Irreversible — no safe recovery path |
| `TRUNCATE TABLE` | Deletes all rows — irreversible |
| `SHUTDOWN` | Would terminate the HANA instance |
| `ALTER SYSTEM ...` | Modifies HANA system configuration — admin territory |
| `DELETE` without a `WHERE` clause | Full table delete with no filter |
| Multi-statement SQL (`;` separator) | Prevents batched destructive operations |

### Controlled by write_mode

Everything else that is not a plain `SELECT` or `WITH` — `INSERT`, `UPDATE`, `CREATE`, `MERGE`, `ALTER TABLE`, `CALL`, and similar — is handled by your `write_mode` setting:

| write_mode | Behaviour |
|------------|-----------|
| `deny` | All non-read-only SQL is blocked. Read-only exploration only. |
| `ask` *(recommended)* | Claude pauses and shows you the SQL before executing. You see the statement before it runs. |
| `allow` | Writes execute automatically. The always-blocked list above still applies. |

Start with `ask`. Switch to `allow` for a specific session once you trust the workflow for that task.

> **Knowledge graph builds use reviewed writes.** When `knowledge-graph-builder` creates VERTICES, EDGES, and TRIPLES tables, each CREATE TABLE and INSERT goes through the write guard exactly like any other write. Set `write_mode = ask` to review each step.

---

## First-run verification

```
/sap-hana-cloud:connection-doctor
```

Confirms the MCP server can reach your HANA endpoint and that credentials work. If this succeeds, proceed to:

```
/sap-hana-cloud:landscape-recon
/sap-hana-cloud:write-safety-primer
```

---

## Knowledge graph and SPARQL

The plugin can build a HANA-native knowledge graph from any schema. The graph is stored as three tables in your work schema and can be queried via SPARQL 1.1 or HANA GRAPH statements.

### What the graph stores

| Table | Purpose | Query via |
|-------|---------|-----------|
| `KG_<SCHEMA>_VERTICES` | One row per table — entity type, row count, column count, IRI | HANA GRAPH queries |
| `KG_<SCHEMA>_EDGES` | One row per relationship — FK or inferred, with confidence and predicate IRI | HANA GRAPH queries |
| `KG_<SCHEMA>_TRIPLES` | RDF triple store — subject, predicate, object, graph URI, IS_LITERAL, DATATYPE | SPARQL 1.1 / SQL |

### RDF namespace conventions

| Prefix | IRI | Used for |
|--------|-----|---------|
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | Type assertions, containers |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` | Labels, subclass declarations |
| `owl:` | `http://www.w3.org/2002/07/owl#` | Ontology classes and properties |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | Column datatype ranges |
| `hana:` | `http://sap.com/hana/ontology#` | Plugin-defined ontology classes (FactTable, DimensionTable, etc.) |
| `hanat:` | `http://sap.com/hana/schema/<SCHEMA>#` | Instance IRIs for tables in this schema |

### SPARQL execution — three options

#### Option A: SQL queries on the TRIPLES table (always available, no extra setup)

Executes standard SQL joins over the TRIPLES table. Works on any HANA instance where the plugin has written the knowledge graph.

```sql
-- Find all entity types
SELECT SUBJECT, OBJECT AS ENTITY_TYPE
FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES"
WHERE PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND IS_LITERAL = 0;

-- Find all FACT tables
SELECT SUBJECT AS TABLE_IRI
FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES"
WHERE PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND OBJECT = 'http://sap.com/hana/ontology#FactTable';

-- Find all direct relationships and their types
SELECT
  S.SUBJECT AS SOURCE_TABLE,
  T.OBJECT  AS RELATIONSHIP_TYPE,
  R.OBJECT  AS TARGET_TABLE
FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES" S
JOIN "<work_schema>"."KG_<SCHEMA>_TRIPLES" T
  ON S.SUBJECT = T.SUBJECT
  AND T.PREDICATE = 'http://sap.com/hana/ontology#relationshipType'
JOIN "<work_schema>"."KG_<SCHEMA>_TRIPLES" R
  ON S.SUBJECT = R.SUBJECT
  AND R.PREDICATE = 'http://sap.com/hana/ontology#relatesTo'
WHERE S.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
```

#### Option B: SPARQL 1.1 via HANA Graph Service REST API (requires Graph Engine)

Use this if HANA Graph Engine is provisioned in your HANA Cloud instance.

**Endpoint:** `https://<host>/v1/query/<tenant>/graphs/KG_<SCHEMA>/sparql`  
**Method:** `POST`  
**Content-Type:** `application/sparql-query`  
**Accept:** `application/sparql-results+json`  
**Auth:** Basic auth or OAuth with your HANA credentials

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX hana: <http://sap.com/hana/ontology#>

# Find all entities and their types
SELECT ?entity ?type WHERE {
  ?entity rdf:type ?type .
  FILTER(STRSTARTS(STR(?type), "http://sap.com/hana/ontology#"))
}

# Find all direct table-to-table relationships
SELECT ?source ?target ?relType WHERE {
  ?source hana:relatesTo ?target .
  ?source hana:relationshipType ?relType .
}

# Find 1-hop neighbourhood of a specific table
SELECT ?neighbour ?relType WHERE {
  <http://sap.com/hana/schema/<SCHEMA>#MY_TABLE> hana:relatesTo ?neighbour .
  <http://sap.com/hana/schema/<SCHEMA>#MY_TABLE> hana:relationshipType ?relType .
}

# CONSTRUCT: export subgraph of all fact table relationships
CONSTRUCT {
  ?s hana:relatesTo ?o .
}
WHERE {
  ?s rdf:type hana:FactTable .
  ?s hana:relatesTo ?o .
}
```

#### Option C: HANA GRAPH queries on the property graph (requires DBA to create GRAPH WORKSPACE)

After a DBA creates the GRAPH WORKSPACE with the DDL provided by `knowledge-graph-builder`, you can run GRAPH traversal queries:

```sql
-- Run after: CREATE GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>" ...

-- Traverse all 1-hop relationships from a given table node
GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
MATCH (src)-[e]->(tgt)
WHERE src.TABLE_NAME = 'ORDERS'
RETURN src.TABLE_NAME AS SOURCE, e.RELATIONSHIP_TYPE, tgt.TABLE_NAME AS TARGET;

-- Find all FACT table nodes
GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
MATCH (v)
WHERE v.ENTITY_TYPE = 'FACT'
RETURN v.TABLE_NAME, v.ROW_COUNT;

-- Find tables two hops away from a starting node
GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
MATCH (src)-[*1..2]->(tgt)
WHERE src.TABLE_NAME = 'ORDERS'
RETURN DISTINCT tgt.TABLE_NAME;
```

### GRAPH WORKSPACE DDL (DBA privilege required)

The `knowledge-graph-builder` skill generates this statement as a display-only artifact. A DBA or GRAPH ADMIN must run it:

```sql
CREATE GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
  EDGE TABLE "<work_schema>"."KG_<SCHEMA>_EDGES"
    SOURCE COLUMN "SOURCE_VERTEX_ID"
    TARGET COLUMN "TARGET_VERTEX_ID"
    KEY COLUMN "EDGE_ID"
  VERTEX TABLE "<work_schema>"."KG_<SCHEMA>_VERTICES"
    KEY COLUMN "VERTEX_ID";
```

### Required privileges for knowledge graph

| Action | Required privilege |
|--------|-------------------|
| SYS catalog queries (FK discovery, view/proc discovery, lineage) | `CATALOG READ` system privilege |
| Creating KG tables in work schema | `CREATE TABLE`, `INSERT` on work schema |
| Creating GRAPH WORKSPACE | `GRAPH ADMIN` or `DBA` role |
| Querying via Graph Service REST | HANA Graph Engine provisioned + HANA credentials |

### Knowledge graph workflow

```
/sap-hana-cloud:relationship-discoverer   → discover FK + naming-pattern edges
/sap-hana-cloud:entity-classifier         → classify tables as FACT/DIMENSION/MASTER/REFERENCE/STAGING
/sap-hana-cloud:ontology-planner          → produce Turtle (.ttl) + JSON-LD @context
/sap-hana-cloud:knowledge-graph-builder   → materialize VERTICES, EDGES, TRIPLES in work schema
```

Or use the `hana-ontologist` agent to run the entire pipeline in one conversation:

```
@hana-ontologist Build a knowledge graph for the SALES schema and show me SPARQL queries
```

---

## Skills reference

### Setup and discovery

| Skill | Description |
|-------|-------------|
| `connection-doctor` | Diagnose HANA connection problems. Start here when something is broken. |
| `plugin-doctor` | Confirm the write hook is active, work schema is configured, and MCP tools are available. |
| `landscape-recon` | List all accessible schemas. Shows table and view counts per schema. Identifies domain vs system schemas. |
| `schema-recon` | Summarise one schema — table types, row counts, candidate key patterns, and suggested starting tables. |
| `table-explorer` | End-to-end inspection of one table — columns, data types, nullable flags, indexes, and 5 sample rows. |
| `semantics-bootstrap` | Create or extend a semantics JSON file with table and column meanings, used to give Claude curated context. |

### Querying and analysis

| Skill | Description |
|-------|-------------|
| `query-builder` | Guide from a business question to a working HANA SQL query. Confirms table, columns, grain, and filters before writing SQL. |
| `sql-preview-runner` | Run arbitrary SQL conservatively — previews before committing, adds `TOP` limits automatically. |
| `join-hypothesis` | Find likely join keys between two HANA tables based on column name and type matching. |
| `schema-diff` | Compare the column schemas of two tables side by side — matching columns, type differences, and missing columns. |
| `column-investigator` | Profile one column for meaning, null rate, distinct values, and data type consistency. |
| `quality-scan` | Lightweight quality scan of one table — key uniqueness, null rates, constant columns, date range sanity. |
| `index-review` | Inspect table indexes, identify missing indexes for common query patterns, and flag performance implications. |

### Ontology and knowledge graph

| Skill | Description |
|-------|-------------|
| `relationship-discoverer` | Queries `SYS.REFERENTIAL_CONSTRAINTS` for FK constraints and `SYS.TABLE_COLUMNS` for naming-pattern implicit edges. Outputs a labeled edge list (CONFIRMED / INFERRED). First step in the KG pipeline. |
| `entity-classifier` | Classifies every table in a schema as FACT, DIMENSION, MASTER, REFERENCE, STAGING, or ANALYTICAL using row count, column patterns, and name heuristics. |
| `ontology-planner` | Produces a Turtle (.ttl) ontology (TBox only — classes and properties, no instance data) and a JSON-LD `@context` block from entity classification and relationship discovery results. |
| `knowledge-graph-builder` | End-to-end knowledge graph materialization. Creates VERTICES + EDGES tables (for HANA GRAPH queries) and a TRIPLES table (RDF triple store for SPARQL 1.1). Generates GRAPH WORKSPACE DDL and all three SPARQL execution options. All writes go through the write guard. |
| `column-cross-mapper` | Queries `SYS.TABLE_COLUMNS` to find all columns shared across multiple tables. Ranks by occurrence count, classifies as HUB_KEY / SHARED_DOMAIN / AUDIT / AMBIGUOUS. Fastest way to discover implicit relationships when FK constraints are absent. |

### Schema discovery and lineage

| Skill | Description |
|-------|-------------|
| `view-explorer` | Discovers and describes SQL views and HANA Calculation Views via `SYS.VIEWS` and `SYS.VIEW_COLUMNS`. Groups by type; extracts source tables from SQL view definitions. |
| `procedure-catalog` | Lists stored procedures and scalar/table functions via `SYS.PROCEDURES` and `SYS.FUNCTIONS`. Identifies PAL algorithm procedures automatically. Flags invalid objects. |
| `lineage-graph` | Traces object dependencies 3 levels upstream and downstream using `SYS.OBJECT_DEPENDENCIES`. Identifies shared nodes (high fan-in) and cross-schema references. Outputs a Mermaid flowchart. |

### Extended profiling and cataloging

| Skill | Description |
|-------|-------------|
| `full-schema-profiler` | Multi-table data catalog profiler. For each table in a schema, collects row counts, key column null rates, date ranges, and status column cardinality in one pass. Uses `SYS.M_TABLE_STATISTICS` for fast row counts. |
| `temporal-coverage-scan` | Analyzes all DATE and TIMESTAMP columns across selected tables. Computes EARLIEST, LATEST, HISTORY_DAYS, and STALENESS_DAYS per table. Flags cross-table temporal misalignments. |
| `distribution-analyzer` | Value distribution analysis for categorical/code columns. Shows top 15 values, null rates, suspicious null-encoded strings, and cardinality. Generates `owl:oneOf` candidate lists for ontology use. |

### Reviewed writes

| Skill | Description |
|-------|-------------|
| `work-schema-bootstrap` | Plan or create a dedicated work schema for feature tables, PAL outputs, KG tables, and staging objects. |
| `write-safety-primer` | Explains the write guard to Claude and confirms the hook is active. Run this before any write session. |
| `write-plan-review` | Turn a requested DDL or DML change into a step-by-step reviewed execution plan with rollback guidance. |
| `reviewed-write-executor` | Execute reviewed DDL/DML through the write guard. The hook intercepts the SQL for confirmation before execution. |
| `merge-upsert-planner` | Design a `MERGE INTO ... USING ... ON ... WHEN MATCHED / NOT MATCHED` workflow with rollback options. |

### BI design

| Skill | Description |
|-------|-------------|
| `star-schema-designer` | Given a business question and a candidate fact table, identifies dimension tables, validates join integrity (LEFT JOIN referential check), and produces a star schema Mermaid diagram and reference SELECT template. |
| `kpi-mapper` | Maps plain-language KPI descriptions to validated SQL expressions (STOCK, FLOW, RATIO, RATE, AVERAGE types). Runs validation previews. Always uses NULLIF for denominators. |
| `data-freshness-dashboard` | Summarises data freshness across key tables: latest record date, staleness in days, rows loaded last 7/30 days. Flags LOAD_GAP and NO_RECENT_LOADS anomalies. Optionally generates a monitoring SQL VIEW. |

### Curated dataset and modeling design

| Skill | Description |
|-------|-------------|
| `curated-dataset-recon` | Shortlist curated HANA tables for a business question. Identifies likely keys, event dates, and measures from metadata. |
| `score-date-design` | Define entity grain, score date, prediction horizon, and leakage boundaries for an ML use case. Classifies columns as SAFE / LEAKAGE / AMBIGUOUS. |
| `training-split-planner` | Design time-aware train / validation / test splits. Produces a CASE-based split SQL template anchored to the score date column. |

### Feature engineering and PAL / hana_ml

| Skill | Description |
|-------|-------------|
| `feature-set-planner` | Design a leakage-aware ML feature set. Produces a feature plan table with aggregation logic, lookback windows, and leakage classification per feature. |
| `feature-table-materializer` | Convert a reviewed feature plan into a materialized HANA table in the work schema. Includes grain verification before CREATE and a postcheck after. |
| `pal-preflight` | End-to-end PAL/hana_ml readiness check: connection, PAL installation, role grants, work schema, and minimum data requirements. |
| `pal-role-checker` | Detailed privilege audit for PAL. Runs catalog queries against `SYS.AFL_FUNCTIONS`, `PUBLIC.GRANTED_ROLES`, and `SYS.EFFECTIVE_PRIVILEGES`. |
| `pal-sql-starter` | Generate a PAL SQL template for a chosen algorithm, ready to adapt and run via `reviewed-write-executor`. |
| `pal-python-starter` | Generate a self-contained Python `hana_ml` script. Covers connection, HANA dataframe, chronological split, fit, predict, and feature importance. Connection values come from environment variables. |
| `hana-ml-feature-flow` | Orchestrate the full pipeline: curated-dataset-recon → score-date-design → feature-set-planner → pal-preflight → feature-table-materializer → feature-output-audit → training-split-planner → pal-python-starter. |
| `feature-output-audit` | Audit a materialized feature table for modeling readiness. Checks grain, null rates, constant columns, and date ranges. Returns READY / REVIEW NEEDED / BLOCKED. |

### Utilities

| Skill | Description |
|-------|-------------|
| `release-smoke-test` | Full 6-stage manual smoke-test sequence covering validation, connection, read-only discovery, write hook behavior (5 sub-tests), and Python starter generation. |

---

## Agents reference

### hana-analyst

**Model:** Sonnet · **Max turns:** 20

Main analysis specialist for schema discovery, table understanding, and query design. Good for open-ended HANA exploration.

Invoke: `@hana-analyst Explore the SALES schema and find the best table for monthly revenue analysis`

### hana-researcher

**Model:** Haiku · **Read-only**

Fast discovery agent. Lists schemas, narrows to relevant tables, identifies keys, dates, and measures. Use for quick orientation before deeper analysis.

Invoke: `@hana-researcher List all schemas and identify candidate tables for customer analytics`

### hana-curated-dataset-scout

**Model:** Haiku · **Read-only**

Fast scout specifically for curated and consumption-ready datasets. Ranks tables by suitability for ML feature source or label source.

Invoke: `@hana-curated-dataset-scout Find the best source tables for churn prediction in the DATA_MART schema`

### hana-quality-reviewer

**Model:** Sonnet · **Read-only**

Reviews tables for trustworthiness and modeling readiness: key uniqueness, null patterns, duplicate detection, value ranges, and leakage risk assessment.

Invoke: `@hana-quality-reviewer Review CUSTOMER_FEATURES for modeling readiness`

### hana-sql-engineer

**Model:** Sonnet · **Max turns:** 20

Specialist for HANA SQL design and query repair. Builds queries incrementally, previews with small row counts, and avoids writes unless explicitly instructed.

Invoke: `@hana-sql-engineer Write a query that aggregates order revenue by customer and month for the last 12 months`

### hana-write-operator

**Model:** Sonnet · **Max turns:** 20

Specialist for reviewed DDL and DML: CREATE TABLE AS SELECT, INSERT INTO, MERGE, ALTER TABLE, staging table workflows. Restates every change before execution and prefers the work schema.

Invoke: `@hana-write-operator Create a feature table in ML_WORK schema based on this feature plan: [paste plan]`

### hana-feature-engineer

**Model:** Sonnet · **Max turns:** 20

Specialist for leakage-aware feature engineering. Designs entity grain, score date, history windows, and feature aggregation logic. Classifies columns as SAFE / LEAKAGE / AMBIGUOUS.

Invoke: `@hana-feature-engineer Design a feature set for 30-day failure prediction from the MAINTENANCE_EVENTS table`

### hana-ml-engineer

**Model:** Sonnet · **Max turns:** 20

Bridges HANA metadata discovery with Python `hana_ml` workflows. Generates Python scripts using env-var connections, correct `hana_ml` API patterns, and PAL algorithm imports.

Invoke: `@hana-ml-engineer Generate a Python hana_ml starter for binary classification using the ASSET_FEATURES table`

### hana-pal-operator

**Model:** Sonnet · **Max turns:** 20

Specialist for PAL-oriented SQL planning and role readiness. Checks AFL catalog access, proposes PAL SQL templates, and translates PAL readiness results into actionable next steps.

Invoke: `@hana-pal-operator Check my PAL readiness and generate a GradientBoostingTree SQL starter`

### hana-platform-advisor

**Model:** Sonnet · **Read-only**

Architecture advisor for HANA Cloud decisions: connection types, MDC vs single-container, CAP integration, Fiori service exposure, BTP deployment shape, and feature store design.

Invoke: `@hana-platform-advisor Should I use a single-container or MDC setup for this analytics workload?`

### hana-ontologist

**Model:** Sonnet · **Max turns:** 30

Ontology and knowledge graph pipeline specialist. Orchestrates the full KG build: relationship-discoverer → entity-classifier → ontology-planner → knowledge-graph-builder. Generates SPARQL queries and explains all three HANA execution options. Knows HANA IRI namespace conventions and GRAPH WORKSPACE DDL requirements.

Invoke: `@hana-ontologist Build a knowledge graph for the SALES schema and produce SPARQL queries I can run today`

### hana-data-cataloger

**Model:** Sonnet · **Read-only · Max turns:** 25

Comprehensive data catalog builder. Profiles all tables in a schema — structure, entity classification, temporal coverage, distribution, and semantic annotation status. Produces a catalog card per table. Good for first-time schema assessment or handoff documentation.

Invoke: `@hana-data-cataloger Build a complete data catalog for the ANALYTICS schema`

### hana-bi-architect

**Model:** Sonnet · **Read-only · Max turns:** 20

BI layer design specialist. Identifies fact and dimension tables, validates join integrity, designs star/snowflake schemas, maps business KPIs to SQL, and produces a BI design document with CREATE VIEW stubs for review. Advisory only — no writes.

Invoke: `@hana-bi-architect Design a BI layer for monthly revenue and customer segmentation reporting from the SALES schema`

---

## Examples

The `examples/` directory contains ready-to-adapt files:

| File | Description |
|------|-------------|
| `feature_table_materialization.sql` | Customer churn feature table CTAS — simple grain, 4 behavioral features |
| `pal_feature_pipeline_hana_ml.py` | Python `hana_ml` starter for a customer churn feature table |
| `asset_health_feature_pipeline.sql` | Asset health failure prediction CTAS — 7 features, explicit score date grid, multi-source joins |
| `asset_health_hana_ml.py` | Python `hana_ml` starter for asset health — chronological split, GBT training, feature importance |
| `hana-semantics.example.json` | Semantics overlay JSON example for the customer tables |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `npx: command not found` | Node.js not installed or not on PATH | Install Node.js 18+ |
| `Cannot connect to HANA host` | Wrong host or port, or firewall blocking the connection | Verify host/port with a direct JDBC connection test |
| `Invalid credentials` | Wrong user or password | `/plugin config sap-hana-cloud` and re-enter credentials |
| TLS certificate errors | Self-signed certificate on on-prem HANA | Set Validate Certificate to `false` |
| Plugin tools not visible | Plugin not loaded | `/reload-plugins` |
| Write hook not triggering | Hook file modified or path wrong | `/sap-hana-cloud:plugin-doctor` |
| DROP TABLE not blocked | Write guard regression | Run the write guard test from `release-smoke-test` and check `hana_sql_guard.py` |
| PAL functions inaccessible | Missing AFL role grants | `/sap-hana-cloud:pal-role-checker` for the specific grant list to request from a DBA |
| hana_ml import errors | hana-ml not installed in active Python env | `pip install hana-ml` in your project virtual environment |
| `SYS.REFERENTIAL_CONSTRAINTS` access denied | Missing CATALOG READ | Request `CATALOG READ` system privilege for your technical user |
| `SYS.OBJECT_DEPENDENCIES` access denied | Missing CATALOG READ | Same — `CATALOG READ` covers all SYS catalog tables |
| KG VERTICES/EDGES table not created | work_schema not configured, or write_mode = deny | `/sap-hana-cloud:work-schema-bootstrap`, then set write_mode to `ask` |
| GRAPH WORKSPACE creation fails | Missing DBA or GRAPH ADMIN privilege | Ask a DBA to run the DDL shown by `knowledge-graph-builder` |
| SPARQL endpoint returns 404 | Graph Engine not provisioned in HANA Cloud | Use Option A (SQL on TRIPLES table) instead, or provision Graph Engine via HANA Cloud Central |

---

## Uninstall

```
/plugin uninstall sap-hana-cloud
```

This removes the plugin and all stored credentials.

---

## Backend server

This plugin contains no HANA connectivity code. The MCP server is an independent open-source project:

**Repository:** [github.com/HatriGt/hana-mcp-server](https://github.com/HatriGt/hana-mcp-server)  
**Package:** `hana-mcp-server` (npm)  
**Author:** [@HatriGt](https://github.com/HatriGt)  
**License:** MIT

The plugin author (Rahul Sethi) is not affiliated with the `hana-mcp-server` project. Plugin issues should be reported to this repository. MCP server issues (HANA connectivity, tool behaviour) should be reported to the `hana-mcp-server` repository.
