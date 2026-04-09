# claude_plugins — Rahul Sethi's Claude Code Plugin Marketplace

A Claude Code marketplace hosting production-ready plugins for enterprise data and analytics workflows.
Plugins in this marketplace are thin Claude Code wrappers around existing backend tools — they do not reimplement backend logic.

**Marketplace identifier:** `sethir-marketplace`

---

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [sap-datasphere](./plugins/sap-datasphere/) | 1.0.0-beta.2 | Claude Code plugin for SAP Datasphere — 20 skills, 5 agents |

---

## sap-datasphere Plugin

A Claude Code plugin that wraps the [SAP Datasphere MCP server](https://github.com/rahulsethi/SAPDatasphereMCP) and exposes it through workflow-oriented skills and agents.

### What it does

- Launches the `sap-datasphere-mcp` CLI as a managed MCP server inside Claude Code
- Collects Datasphere connection credentials via Claude's secure `userConfig` — no file editing required
- Provides 20 skills covering orientation, asset exploration, querying, data quality, and governance
- Provides 5 subagents for analysis, research, querying, quality review, and data stewardship

### Prerequisites

1. **Claude Code** — installed and up to date
2. **SAP Datasphere MCP server** CLI available in your shell:

```bash
pip install mcp-sap-datasphere-server
# or
pipx install mcp-sap-datasphere-server
```

Verify:

```bash
sap-datasphere-mcp --version
```

3. **SAP Datasphere OAuth client** — a technical user with an OAuth client ID and secret from BTP Cockpit

---

## Installation

### From this GitHub marketplace (recommended)

Inside a Claude Code session:

```text
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

### From local clone

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
```

Then inside Claude Code:

```text
/plugin marketplace add ./
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

---

## Configuration

On install, Claude prompts for the following values. They are stored securely in Claude's plugin config store — nothing is written to disk.

| Field | Description |
|-------|-------------|
| **Tenant URL** | `https://<your-tenant>.eu10.hcs.cloud.sap` |
| **OAuth Token URL** | `https://<your-tenant>.authentication.eu10.hana.ondemand.com/oauth/token` |
| **Client ID** | OAuth client ID from BTP Cockpit |
| **Client Secret** | OAuth client secret (stored encrypted) |
| **Verify TLS** | `1` to verify certificates (recommended), `0` for proxy environments |
| **Mock Mode** | `0` for live tenant, `1` for offline testing |

To update credentials after install:

```text
/plugin config sap-datasphere
```

---

## Skills

### Orientation and discovery
| Skill | What it does |
|-------|-------------|
| `tenant-recon` | Diagnose the tenant, list spaces, summarise a promising space |
| `space-recon` | Summarise a single space and suggest starting assets |
| `orientation-path` | Fastest path from zero context to a viable first query |
| `cross-space-search` | Search a business concept across every space in the tenant |

### Asset exploration
| Skill | What it does |
|-------|-------------|
| `asset-search` | Search for assets by business concept within a space |
| `asset-explorer` | Inspect one asset end-to-end — metadata, columns, schema, preview |
| `asset-card` | Produce a concise semantic summary card for an asset |
| `compare-assets` | Compare two assets for structural similarity and join potential |
| `schema-diff` | Side-by-side column schema comparison with join key analysis |

### Querying and analysis
| Skill | What it does |
|-------|-------------|
| `query-builder` | Guide from a business question to a working relational or analytical query |
| `analytical-check` | Verify analytical query support and run a sample analytical query |
| `kpi-finder` | Identify candidate KPI and measure columns in a space |

### Data quality and governance
| Skill | What it does |
|-------|-------------|
| `data-quality-scan` | Lightweight data quality scan using preview, schema, and profiling |
| `column-investigator` | Profile key columns for nulls, cardinality, and outliers |
| `full-space-audit` | Comprehensive health and readiness audit of all assets in a space |

### Advanced
| Skill | What it does |
|-------|-------------|
| `join-hypothesis` | Find shared columns across assets and suggest likely joins |
| `lineage-explorer` | Trace how a key column flows across assets in a space |

### Utilities
| Skill | What it does |
|-------|-------------|
| `mock-mode-demo` | Safe demo flow using mock mode — no live tenant required |
| `plugin-doctor` | Diagnose MCP setup and connectivity problems |
| `release-smoke-test` | Manual smoke test sequence for release validation |

---

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `datasphere-analyst` | sonnet | Main analysis specialist — orientation through query |
| `datasphere-researcher` | haiku | Lightweight discovery — shortlist spaces and assets |
| `datasphere-quality-reviewer` | sonnet | Read-only quality and profiling reviewer |
| `datasphere-query-assistant` | sonnet | Interactive guide from business question to executable query |
| `datasphere-data-steward` | sonnet | Data governance and trust assessment (LOW/MEDIUM/HIGH) |

---

## Recommended first steps

After installing and configuring the plugin:

```text
/sap-datasphere:tenant-recon
/sap-datasphere:cross-space-search
/sap-datasphere:query-builder
```

---

## Repository structure

```
claude_plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest
├── .mcp.json                     # Dev-only local MCP server (uses shell env vars)
├── CLAUDE.md                     # Working rules for Claude Code sessions
├── plugins/
│   └── sap-datasphere/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest with userConfig schema
│       ├── .mcp.json             # Plugin MCP launcher (uses ${user_config.*})
│       ├── skills/               # 20 workflow skills
│       ├── agents/               # 5 subagents
│       ├── CHANGELOG.md
│       └── README.md
├── docs/                         # Developer and optimization notes
└── smoke_test.py                 # Mock-mode smoke test (requires venv)
```

---

## Backend server

The MCP backend is maintained separately:
[github.com/rahulsethi/SAPDatasphereMCP](https://github.com/rahulsethi/SAPDatasphereMCP)

This plugin repo contains no backend Python code.
