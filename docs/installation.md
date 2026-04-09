# Installation Guide — sap-datasphere Plugin

## Prerequisites

### 1. Claude Code
Install or update to the latest version:
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. SAP Datasphere MCP server
The plugin launches `sap-datasphere-mcp` as a managed MCP process. Install it before adding the plugin:

```bash
pip install mcp-sap-datasphere-server
# or with pipx (recommended for CLI tools)
pipx install mcp-sap-datasphere-server
```

Verify the CLI is on your PATH:
```bash
sap-datasphere-mcp --version
```

### 3. SAP Datasphere OAuth client
You need a technical user OAuth client from BTP Cockpit with:
- Client ID
- Client Secret
- Token URL (`https://<tenant>.authentication.<region>.hana.ondemand.com/oauth/token`)

---

## Install from GitHub marketplace

Open a Claude Code session and run:

```text
/plugin marketplace add rahulsethi/claude_plugins
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

Claude will prompt for the following configuration values:

| Field | Example |
|-------|---------|
| Tenant URL | `https://your-tenant.eu10.hcs.cloud.sap` |
| OAuth Token URL | `https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token` |
| Client ID | from BTP Cockpit OAuth client |
| Client Secret | from BTP Cockpit OAuth client (stored encrypted) |
| Verify TLS | `1` (recommended) |
| Mock Mode | `0` for live, `1` for offline testing |

Values are stored in Claude's secure plugin config store. Nothing is written to disk.

---

## First-run verification

After install, confirm the plugin is working:

```text
/sap-datasphere:tenant-recon
```

This skill runs diagnostics, lists spaces, and summarises a promising space.

---

## Update credentials

```text
/plugin config sap-datasphere
```

---

## Uninstall

```text
/plugin uninstall sap-datasphere
```

This removes the plugin and all stored credentials.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `sap-datasphere-mcp: command not found` | CLI not installed or not on PATH | `pip install mcp-sap-datasphere-server` |
| `401 Unauthorized` | Wrong client ID or secret | `/plugin config sap-datasphere` |
| TLS handshake errors | Corporate TLS-inspection proxy | Set Verify TLS to `0` |
| Mock responses in live session | Mock Mode left at `1` | `/plugin config sap-datasphere` → set Mock Mode to `0` |
| Plugin not found after install | Plugin cache not refreshed | `/reload-plugins` |
