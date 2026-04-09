# UserConfig Migration: Credential Management via Plugin Config
**Date:** 2026-04-09
**Scope:** Wire SAP Datasphere plugin credentials through Claude plugin userConfig instead of manual file edits.

---

## What Changed

### `plugins/sap-datasphere/.claude-plugin/plugin.json`

Added `userConfig` block with six fields. Each field now includes the required `title` and `type` properties that the plugin validator enforces. The `client_secret` field is marked `"sensitive": true` so Claude stores it encrypted and never echoes it in logs or UI.

| Field | Title | Type | Sensitive |
|---|---|---|---|
| `tenant_url` | Tenant URL | string | no |
| `oauth_token_url` | OAuth Token URL | string | no |
| `client_id` | Client ID | string | no |
| `client_secret` | Client Secret | string | **yes** |
| `verify_tls` | Verify TLS | string | no |
| `mock_mode` | Mock Mode | string | no |

> `verify_tls` and `mock_mode` use `string` (not `boolean`) because the MCP server reads them as env vars and compares against `"1"` / `"0"`.

### `plugins/sap-datasphere/.mcp.json`

Already uses `${user_config.*}` substitution syntax — no changes required.

```json
{
  "sap-datasphere": {
    "command": "sap-datasphere-mcp",
    "args": [],
    "env": {
      "DATASPHERE_TENANT_URL": "${user_config.tenant_url}",
      "DATASPHERE_OAUTH_TOKEN_URL": "${user_config.oauth_token_url}",
      "DATASPHERE_CLIENT_ID": "${user_config.client_id}",
      "DATASPHERE_CLIENT_SECRET": "${user_config.client_secret}",
      "DATASPHERE_VERIFY_TLS": "${user_config.verify_tls}",
      "DATASPHERE_MOCK_MODE": "${user_config.mock_mode}"
    }
  }
}
```

### Root `.mcp.json` (dev-only)

Unchanged — still reads shell env vars (`${DATASPHERE_*}`) for developer use. Real credentials are supplied via shell environment and never committed.

---

## Validation Results

```
claude plugin validate .
  -> Validates marketplace manifest
  -> Exit 0 (passed with 1 warning: no marketplace description — known, non-blocking)

claude plugin validate ./plugins/sap-datasphere
  -> Exit 0, no errors, no warnings
```

> MCP server addition step skipped per session instructions (server addition is disabled in this environment).

---

## Key Design Decision

No real credential values appear in any version-controlled file. The mapping is:

```
Version-controlled .mcp.json   →   ${user_config.tenant_url}  (template placeholder)
Claude plugin config store     →   actual value, stored by Claude per user
```

The root `.mcp.json` (dev mode) uses shell env vars so developer credentials live in `.env` / shell profile, outside the repo.
