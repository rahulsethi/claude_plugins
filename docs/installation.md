# Installation Overview

This page summarises all installation methods for the `sethir-marketplace` plugins. For full details, prerequisites, and configuration references, see the plugin-specific guides:

- [SAP Datasphere — full guide](sap-datasphere.md)
- [SAP HANA Cloud — full guide](sap-hana-cloud.md)

---

## Prerequisites summary

| Requirement | sap-datasphere | sap-hana-cloud |
|-------------|----------------|----------------|
| Claude Code | ✓ | ✓ |
| Python + `mcp-sap-datasphere-server` | ✓ | — |
| Node.js 18+ | — | ✓ |
| SAP Datasphere OAuth client | ✓ | — |
| HANA technical user | — | ✓ |
| `CATALOG READ` system privilege | — | For SYS catalog queries (views, FK discovery, lineage, ontology) |
| Python + `hana-ml` (optional) | — | For ML generation only |
| HANA Graph Engine (optional) | — | For SPARQL endpoint; SQL-on-TRIPLES works without it |

---

## Method 1 — From GitHub marketplace (recommended for both plugins)

Open a Claude Code session and run:

```
/plugin marketplace add rahulsethi/claude_plugins
```

Then install the plugin you want:

```
/plugin install sap-datasphere@sethir-marketplace
```
```
/plugin install sap-hana-cloud@sethir-marketplace
```

Reload:

```
/reload-plugins
```

Claude Code will prompt you to enter configuration values (connection credentials, etc.). These are stored securely in Claude's plugin config store — not in any file on disk.

---

## Method 2 — From local clone

Clone this repository, then point Claude at it as a local marketplace:

```bash
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins
```

Inside Claude Code opened in the cloned directory:

```
/plugin marketplace add ./
/plugin install sap-datasphere@sethir-marketplace
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
```

---

## Method 3 — Direct plugin-dir (single session, no marketplace)

Load a plugin directly without installing it through a marketplace. Useful for testing or for users who do not want marketplace registration.

```bash
# For SAP Datasphere:
claude --plugin-dir ./plugins/sap-datasphere

# For SAP HANA Cloud:
claude --plugin-dir ./plugins/sap-hana-cloud
```

Set credentials as shell environment variables before launching. See the full credential lists in each plugin guide.

---

## Method 4 — npx MCP server only (sap-hana-cloud, no plugin wrapper)

If you want the raw HANA MCP tools without the plugin's skills, agents, or write guard — for example, to use `hana-mcp-server` alongside your own prompts:

```bash
claude mcp add sap-hana-cloud npx -y hana-mcp-server
```

Then configure credentials in Claude Code's MCP environment settings. This provides direct access to the HANA MCP tools (`hana_list_schemas`, `hana_describe_table`, `hana_execute_query`, etc.) without the plugin layer.

> **Note:** Without the plugin, the write guard hook is not active. All SQL submitted via `hana_execute_query` will execute without interception, including destructive statements. The knowledge graph skills, ontology pipeline, and all other plugin skills are also unavailable. Use Method 1, 2, or 3 to get the full plugin.

---

## Managing credentials after install

```
/plugin config sap-datasphere
/plugin config sap-hana-cloud
```

---

## Updating plugins

```
/plugin update sap-datasphere@sethir-marketplace
/plugin update sap-hana-cloud@sethir-marketplace
/reload-plugins
```

---

## Uninstalling

```
/plugin uninstall sap-datasphere
/plugin uninstall sap-hana-cloud
```

---

## Troubleshooting quick reference

| Symptom | Fix |
|---------|-----|
| Plugin not found after install | `/reload-plugins` |
| Skills not showing in `/help` | Ensure plugin is listed under an active marketplace |
| Connection refused or timeout | Check host, port, and network access |
| `sap-datasphere-mcp: command not found` | `pip install mcp-sap-datasphere-server` |
| `npx: command not found` (HANA) | Install Node.js 18+ |
| Credentials rejected | `/plugin config <plugin-name>` and re-enter |

Full troubleshooting: [sap-datasphere.md#troubleshooting](sap-datasphere.md#troubleshooting) · [sap-hana-cloud.md#troubleshooting](sap-hana-cloud.md#troubleshooting)
