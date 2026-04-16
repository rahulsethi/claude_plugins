# sap-hana-cloud Plugin Rules

## Purpose
This plugin is a thin Claude Code wrapper around the published `hana-mcp-server` package.

## Boundaries
- Do not copy backend Node.js code from `HatriGt/hana-mcp-server` into this plugin.
- Keep the plugin focused on setup, orchestration, guardrails, skills, agents, and examples.
- `.mcp.json` must use the server name as the top-level key directly. Do **not** add a `mcpServers` wrapper in this repo.
- Use `${user_config.*}` substitutions in `.mcp.json` and plugin hook commands.
- Every `userConfig` field in `plugin.json` must include `title`, `description`, `type`, and `sensitive`.

## Write functionality rules
- This plugin intentionally supports write workflows, but only as **reviewed** DDL and DML.
- The shipped `PreToolUse` hook must stay in place. It guards `hana_execute_query` and forces confirmation or denial for non-`SELECT` and non-`WITH` SQL.
- Keep destructive commands blocked by default in the hook script.
- Write-oriented skills must tell the user which schema will change and what the rollback path is.
- Prefer the dedicated work schema `${user_config.work_schema}` for feature tables, PAL output tables, and staging objects.

## HANA ML and PAL rules
- There are no native PAL MCP tools in the backend today.
- HANA ML support in this plugin means: metadata discovery, feature planning, PAL preflight checks, SQL template generation, and Python `hana_ml` starter generation.
- Do not pretend that PAL execution is magical. Make it clear whether the action is done through `hana_execute_query` or through generated Python using `hana_ml`.

## Current state (0.3.0-alpha.1)
- Skills: 44
- Agents: 13
- Hooks: 1 write-guard `PreToolUse` hook
- Example assets: semantics JSON, feature materialization SQL, and Python `hana_ml` starter

## Knowledge graph and ontology rules
- Knowledge graph tables (VERTICES, EDGES, TRIPLES) live exclusively in `work_schema`. Never write graph tables into source schemas.
- The TRIPLES table follows the W3C RDF model (SUBJECT, PREDICATE, OBJECT + GRAPH_URI, IS_LITERAL, DATATYPE). Do not change this structure.
- IRI namespace: `http://sap.com/hana/ontology#` for ontology classes and properties; `http://sap.com/hana/schema/<SCHEMA_NAME>#` for instance IRIs.
- The `CREATE GRAPH WORKSPACE` DDL requires DBA or GRAPH ADMIN privilege — always present it as a display-only artifact, never execute it through `hana_execute_query`.
- SPARQL queries against the TRIPLES table can be executed three ways: (A) SQL joins on the TRIPLES table (always available), (B) HANA Graph Service REST API (requires Graph Engine), (C) SPARQL_EXECUTE procedure (HANA 2.0 SPS05+). Skills must always provide Option A as a fallback.
- Inferred relationship edges (naming-pattern matches) always carry CONFIDENCE = 'MEDIUM' or 'LOW'. Never promote to CONFIRMED without explicit FK constraint evidence.
- The full KG pipeline order is: `relationship-discoverer` → `entity-classifier` → `ontology-planner` → `knowledge-graph-builder`.

## Skill design rules
- Skills should orchestrate only the current HANA MCP tool surface: `hana_show_config`, `hana_test_connection`, `hana_show_env_vars`, `hana_list_schemas`, `hana_list_tables`, `hana_describe_table`, `hana_explain_table`, `hana_list_indexes`, `hana_describe_index`, `hana_execute_query`, and `hana_query_next_page`. HANA ML support must therefore be built from metadata discovery, reviewed SQL, PAL readiness checks, and generated Python or SQL starters.
- SYS catalog tables (`SYS.REFERENTIAL_CONSTRAINTS`, `SYS.TABLE_COLUMNS`, `SYS.VIEWS`, `SYS.VIEW_COLUMNS`, `SYS.PROCEDURES`, `SYS.PROCEDURE_PARAMETERS`, `SYS.FUNCTIONS`, `SYS.OBJECT_DEPENDENCIES`, `SYS.M_TABLE_STATISTICS`) are accessible via `hana_execute_query`. Always mention `CATALOG READ` as the required privilege when these queries may fail.
- Keep instructions operational and sequence-based.
- Prefer small previews, explicit limits, and schema checks before writes.
- Mention graceful fallback behavior when a catalog view or role check is not accessible.

## Agent design rules
- Use `haiku` only for lightweight discovery roles.
- Use `sonnet` for the main analyst, SQL, write, and ML roles.
- Read-only agents should disallow `Write` and `Edit`.
- The write-capable agent must still behave conservatively and respect hook-driven approval.

## Validation
- Run `claude plugin validate .`
- Run `claude plugin validate ./plugins/sap-hana-cloud`
- Re-test the write hook after any edits to `hooks/hooks.json` or `scripts/hana_sql_guard.py`

## First manual tests
- `/sap-hana-cloud:connection-doctor`
- `/sap-hana-cloud:landscape-recon`
- `/sap-hana-cloud:table-explorer`
- `/sap-hana-cloud:write-safety-primer`
- `/sap-hana-cloud:reviewed-write-executor`
- `/sap-hana-cloud:curated-dataset-recon`
- `/sap-hana-cloud:feature-set-planner`
- `/sap-hana-cloud:pal-preflight`
- `/sap-hana-cloud:pal-role-checker`
- `/sap-hana-cloud:pal-python-starter`

## Release checklist
- Bump version in `plugins/sap-hana-cloud/.claude-plugin/plugin.json`
- Bump version in root `.claude-plugin/marketplace.json`
- Re-run local `--plugin-dir` testing
- Re-run marketplace install testing
- Re-check the write guard with a harmless `CREATE TABLE` or `CREATE VIEW` attempt in the work schema
