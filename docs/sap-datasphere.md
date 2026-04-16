# SAP Datasphere Plugin — Installation and Reference Guide

**Plugin:** `sap-datasphere` · **Version:** `1.0.0-beta.2` · **Marketplace:** `sethir-marketplace`

This plugin is a thin Claude Code wrapper around the [SAP Datasphere MCP server](https://github.com/rahulsethi/SAPDatasphereMCP). It gives Claude structured, read-only access to your SAP Datasphere tenant — spaces, assets, columns, KPIs, lineage, and data quality — without requiring SQL knowledge or Datasphere UI navigation.

**This plugin is read-only throughout. It does not perform writes, admin actions, or schema changes.**

---

## How it works

```
Claude Code ──► sap-datasphere plugin ──► sap-datasphere-mcp CLI ──► SAP Datasphere API
                (skills, agents)           (MCP server process)        (OAuth + REST)
```

The plugin starts `sap-datasphere-mcp` as a managed MCP subprocess when Claude Code launches. Your credentials are passed to the server via environment variables derived from the plugin's `userConfig`. No credentials are written to files.

---

## Prerequisites

### 1. Claude Code

Install or update to the latest version:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

### 2. SAP Datasphere MCP server

The plugin launches `sap-datasphere-mcp` as a subprocess. Install the package before adding the plugin:

```bash
pip install mcp-sap-datasphere-server
# or with pipx (recommended for isolated CLI tools)
pipx install mcp-sap-datasphere-server
```

Verify the CLI is on your PATH:

```bash
sap-datasphere-mcp --version
```

If this fails, check your Python environment's `Scripts` (Windows) or `bin` (macOS/Linux) directory is on `PATH`.

### 3. SAP Datasphere OAuth client

You need a technical user OAuth client configured in BTP Cockpit:

- **Client ID** — the OAuth client identifier
- **Client Secret** — the client secret (keep this safe)
- **Token URL** — typically `https://<your-tenant>.authentication.<region>.hana.ondemand.com/oauth/token`

The technical user needs read access to the spaces and assets you want Claude to explore. Write access is not required and is not used.

---

## Installation methods

### Method 1 — From GitHub marketplace (recommended)

Open a Claude Code session and run:

```
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

Claude will prompt you to enter configuration values. See the [Configuration](#configuration) section below.

### Method 2 — From local clone

Clone this repository and point Claude at it as a local marketplace:

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
```

Then inside a Claude Code session opened in the cloned directory:

```
/plugin marketplace add ./
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

### Method 3 — Direct plugin-dir (development or offline)

If you only want to test the plugin without installing it via a marketplace:

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
claude --plugin-dir ./plugins/sap-datasphere
```

This loads the plugin for the current session only. Skills and agents are available immediately but no credentials are persisted between sessions. Set credentials as shell environment variables before launching:

```bash
export DATASPHERE_TENANT_URL='https://your-tenant.eu10.hcs.cloud.sap'
export DATASPHERE_OAUTH_TOKEN_URL='https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token'
export DATASPHERE_CLIENT_ID='your-client-id'
export DATASPHERE_CLIENT_SECRET='your$client$secret'
export DATASPHERE_VERIFY_TLS='1'
export DATASPHERE_MOCK_MODE='0'

claude --plugin-dir ./plugins/sap-datasphere
```

> Use single quotes around values containing `$` to prevent shell expansion.

---

## Configuration

When installing through the marketplace, Claude Code prompts for these values. They are stored in Claude's secure plugin config store — not in any file on disk.

| Field | Environment variable | Example | Sensitive |
|-------|---------------------|---------|-----------|
| Tenant URL | `DATASPHERE_TENANT_URL` | `https://your-tenant.eu10.hcs.cloud.sap` | No |
| OAuth Token URL | `DATASPHERE_OAUTH_TOKEN_URL` | `https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token` | No |
| Client ID | `DATASPHERE_CLIENT_ID` | `sb-technical-user!t12345` | No |
| Client Secret | `DATASPHERE_CLIENT_SECRET` | *(your secret)* | **Yes** |
| Verify TLS | `DATASPHERE_VERIFY_TLS` | `1` (recommended) or `0` for proxy environments | No |
| Mock Mode | `DATASPHERE_MOCK_MODE` | `0` for live, `1` for offline demo/testing | No |

**Update credentials at any time:**

```
/plugin config sap-datasphere
```

---

## First-run verification

After installing and configuring, verify the connection:

```
/sap-datasphere:tenant-recon
```

This skill runs diagnostics, confirms the OAuth token exchange works, lists all accessible spaces, and summarises a promising space. If it succeeds, the plugin is ready.

For a safe offline test without a live tenant, set Mock Mode to `1` and run:

```
/sap-datasphere:mock-mode-demo
```

---

## Skills reference

### Orientation and discovery

| Skill | Description |
|-------|-------------|
| `tenant-recon` | Run diagnostics, list all accessible spaces, summarise the most promising one for the current work context |
| `space-recon` | Summarise a single Datasphere space — asset counts, types, and suggested starting points |
| `orientation-path` | Fastest path from zero context to a viable first query — combines diagnostics, space listing, and asset surfacing |
| `cross-space-search` | Search a business concept or entity name across every accessible space in the tenant |

### Asset exploration

| Skill | Description |
|-------|-------------|
| `asset-search` | Search for assets within a space by business concept or partial name |
| `asset-explorer` | End-to-end inspection of one asset — metadata, column list, schema, row preview |
| `asset-card` | Produce a concise semantic summary card: purpose, grain, key columns, relationships |
| `compare-assets` | Compare two assets for structural similarity, shared columns, and join potential |
| `schema-diff` | Side-by-side column schema comparison with key column and type analysis |

### Querying and analysis

| Skill | Description |
|-------|-------------|
| `query-builder` | Guide from a business question to a working relational or analytical query — confirms asset, columns, grain, and filter before writing SQL |
| `analytical-check` | Verify whether an asset supports analytical queries and run a sample |
| `kpi-finder` | Identify candidate KPI, measure, and aggregation columns in a space |

### Data quality and governance

| Skill | Description |
|-------|-------------|
| `data-quality-scan` | Lightweight quality scan using column profiling, preview rows, and schema checks |
| `column-investigator` | Profile one key column for null rate, cardinality, outliers, and value distribution |
| `full-space-audit` | Comprehensive health audit of all assets in a space — schema completeness, profiling, quality scores |

### Advanced

| Skill | Description |
|-------|-------------|
| `join-hypothesis` | Identify shared columns across assets in a space and propose likely join relationships |
| `lineage-explorer` | Trace how a key column or concept flows across assets — upstream sources and downstream consumers |

### Utilities

| Skill | Description |
|-------|-------------|
| `mock-mode-demo` | Run a safe demo flow using built-in mock data — no live tenant or credentials needed |
| `plugin-doctor` | Diagnose MCP setup, OAuth connectivity, and common configuration problems |
| `release-smoke-test` | Manual smoke-test sequence for validating a release |

---

## Agents reference

### datasphere-analyst

**Model:** Sonnet · **Role:** Main analysis specialist

Plans and executes the full exploration workflow: tenant orientation → space selection → asset understanding → query design. Good for open-ended data analysis questions.

Invoke: `@datasphere-analyst What are the top revenue sources by region last quarter?`

### datasphere-researcher

**Model:** Haiku · **Role:** Lightweight discovery

Fast discovery agent for scanning spaces, shortlisting relevant assets, and identifying key columns. Use for quick orientation before detailed analysis.

Invoke: `@datasphere-researcher Find all assets related to sales orders in the tenant`

### datasphere-quality-reviewer

**Model:** Sonnet · **Role:** Read-only quality reviewer

Reviews assets for data trust, schema plausibility, null patterns, outlier presence, and governance readiness. Returns a structured quality assessment.

Invoke: `@datasphere-quality-reviewer Review SALES_FACT for modeling readiness`

### datasphere-query-assistant

**Model:** Sonnet · **Role:** Query guide

Interactive guide that walks from a vague business question to a specific, executable query. Confirms grain, columns, and filters at each step before writing SQL.

Invoke: `@datasphere-query-assistant I need a query for monthly active customers by segment`

### datasphere-data-steward

**Model:** Sonnet · **Role:** Data governance

Assesses data completeness, consistency, governance readiness, and analytical fitness. Produces trust ratings (LOW / MEDIUM / HIGH) per asset.

Invoke: `@datasphere-data-steward Assess the CUSTOMER_MASTER asset for governance compliance`

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `sap-datasphere-mcp: command not found` | CLI not installed or not on PATH | `pip install mcp-sap-datasphere-server` then verify `sap-datasphere-mcp --version` |
| `401 Unauthorized` on first tool call | Wrong client ID or secret | `/plugin config sap-datasphere` and re-enter credentials |
| TLS handshake errors | Corporate TLS-inspection proxy intercepting connections | Set Verify TLS to `0` |
| Mock responses appearing in a live session | Mock Mode left at `1` from a previous demo | `/plugin config sap-datasphere` → set Mock Mode to `0` |
| Plugin not found after install | Plugin cache not refreshed | `/reload-plugins` |
| Plugin tools missing in session | Plugin loaded via `--plugin-dir` but env vars not set | Export all `DATASPHERE_*` env vars before launching `claude` |
| `No spaces found` | Technical user does not have space-level read access | Ask Datasphere admin to grant space membership to the technical user |

---

## Uninstall

```
/plugin uninstall sap-datasphere
```

This removes the plugin and all stored credentials from Claude's config store.

---

## Backend server

This plugin contains no backend code. The MCP server is maintained separately:

**Repository:** [github.com/rahulsethi/SAPDatasphereMCP](https://github.com/rahulsethi/SAPDatasphereMCP)  
**Package:** `mcp-sap-datasphere-server`  
**CLI:** `sap-datasphere-mcp`  
**Author:** Rahul Sethi
