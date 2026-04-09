# Enable / Install Flow: sap-datasphere Plugin (userConfig Edition)
**Date:** 2026-04-09
**Applies to:** Plugin version 1.0.0-beta.2 and later (post userConfig migration)

---

## Overview

After the userConfig migration, users no longer edit any files to supply credentials. Claude prompts for them during plugin installation or on first use, stores them securely in its own config store, and injects them as env vars into the MCP server process at runtime.

---

## Pre-requisites

| Requirement | Notes |
|---|---|
| `node` >= 18 | Required by Claude Code CLI |
| `sap-datasphere-mcp` CLI on PATH | Install: `npm install -g mcp-sap-datasphere-server` |
| SAP Datasphere OAuth client | Create a technical user / OAuth client in BTP Cockpit |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |

---

## Install Flow

### Option A — Marketplace Install (recommended for end users)

```bash
# 1. Add the marketplace (one-time, if not already added)
/plugin marketplace add https://github.com/rahulsethi/claude_plugins

# 2. Install the plugin — Claude will prompt for userConfig values
/plugin install sap-datasphere@rahulsethi
```

During step 2 Claude presents a form with all six userConfig fields:

| Prompt | What to enter |
|---|---|
| **Tenant URL** | `https://<your-tenant>.eu10.hcs.cloud.sap` |
| **OAuth Token URL** | `https://<your-tenant>.authentication.eu10.hana.ondemand.com/oauth/token` |
| **Client ID** | Your OAuth client ID from BTP |
| **Client Secret** | Your OAuth client secret (input is masked — stored encrypted) |
| **Verify TLS** | `1` (recommended) or `0` for proxy environments that intercept TLS |
| **Mock Mode** | `0` for live tenant, `1` for offline testing |

After submission Claude stores the values in its secure plugin config store. No file is created or modified in the project directory.

---

### Option B — Local Plugin-Dir (for developers / contributors)

```bash
# 1. Clone this repo
git clone https://github.com/rahulsethi/claude_plugins
cd claude_plugins

# 2. Launch Claude pointing at the plugin directory
claude --plugin-dir ./plugins/sap-datasphere
```

Claude will prompt for the same userConfig fields on first launch.  
Alternatively, export shell env vars and use the root `.mcp.json` dev server (`sap-datasphere-local`) which bypasses userConfig entirely.

```bash
export DATASPHERE_TENANT_URL='https://...'
export DATASPHERE_OAUTH_TOKEN_URL='https://...'
export DATASPHERE_CLIENT_ID='...'
export DATASPHERE_CLIENT_SECRET='...'   # single-quotes prevent $ expansion
export DATASPHERE_VERIFY_TLS='1'
export DATASPHERE_MOCK_MODE='0'
claude
```

---

## Re-configuring Credentials

To update a stored userConfig value after installation:

```bash
/plugin config sap-datasphere
```

Claude presents the same form. Update only the fields that need changing and save. The MCP server will pick up new values on the next tool call (no restart required).

---

## Uninstall

```bash
/plugin uninstall sap-datasphere
```

This removes the plugin and discards all stored userConfig values including the client secret.

---

## How Credentials Flow at Runtime

```
User installs plugin
       |
       v
Claude stores userConfig values (encrypted, per-user)
       |
       v
User invokes a Datasphere skill or agent
       |
       v
Claude starts  sap-datasphere-mcp  process
  env injected:
    DATASPHERE_TENANT_URL       <- ${user_config.tenant_url}
    DATASPHERE_OAUTH_TOKEN_URL  <- ${user_config.oauth_token_url}
    DATASPHERE_CLIENT_ID        <- ${user_config.client_id}
    DATASPHERE_CLIENT_SECRET    <- ${user_config.client_secret}  (sensitive, never logged)
    DATASPHERE_VERIFY_TLS       <- ${user_config.verify_tls}
    DATASPHERE_MOCK_MODE        <- ${user_config.mock_mode}
       |
       v
MCP server authenticates to SAP Datasphere via OAuth
       |
       v
Tool results returned to Claude
```

No credential value ever appears in a version-controlled file or Claude conversation log.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `sap-datasphere-mcp: command not found` | Backend CLI not installed | `npm install -g mcp-sap-datasphere-server` |
| `401 Unauthorized` from Datasphere | Wrong client ID or secret | `/plugin config sap-datasphere` and re-enter credentials |
| TLS handshake errors behind proxy | TLS inspection proxy | Set Verify TLS to `0` via `/plugin config sap-datasphere` |
| Mock tool responses in live session | Mock Mode left at `1` | Set Mock Mode to `0` via `/plugin config sap-datasphere` |
| Validation warning: no marketplace description | Known non-blocking issue | No action needed for plugin users |
