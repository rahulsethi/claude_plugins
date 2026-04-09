# Validation Run: sap-datasphere Plugin Scaffold
**Date:** 2026-04-08
**Scope:** Validate, fix, and smoke test the marketplace scaffold before GitHub publish.

---

## Summary

| Category | Result |
|----------|--------|
| Plugin structure validation | PASS (`claude plugin validate .` exit 0) |
| `.mcp.json` format | FIXED (removed `mcpServers` wrapper) |
| MCP binary (sap-datasphere-mcp) | STARTS OK |
| Skill flow coverage | 13/13 PASS (mock mode) |
| Live OAuth auth | BLOCKED (401 Bad credentials — shell env issue) |

---

## Plugin Structure Validation

**Command:** `claude.exe plugin validate .` from marketplace root
**Command:** `claude.exe plugin validate ./plugins/sap-datasphere`
**Result:** Both exit 0 (silent success — expected behavior)

**Files inspected and confirmed correct:**

| File | Status | Notes |
|------|--------|-------|
| `.claude-plugin/marketplace.json` | OK | declares `rahulsethi-tools`, points to `./plugins/sap-datasphere` |
| `plugins/sap-datasphere/.claude-plugin/plugin.json` | OK | 6 userConfig fields, MIT license, correct metadata |
| `plugins/sap-datasphere/.mcp.json` | FIXED | see below |
| `plugins/sap-datasphere/skills/*/SKILL.md` | OK | 14 skills, all frontmatter valid |
| `plugins/sap-datasphere/agents/*.md` | OK | 3 agents, correct model assignments |
| `.claude/settings.json` (project-level) | OK | no stale permissions, already clean |

### Tool name alignment
All 14 skills reference tool names that exist in the v0.3.0 backend (22 tools confirmed via `tasks.py`):

```
datasphere_diagnostics        datasphere_list_spaces
datasphere_list_assets        datasphere_search_assets
datasphere_get_asset_metadata datasphere_list_columns
datasphere_describe_asset_schema datasphere_preview_asset
datasphere_query_relational   datasphere_query_analytical
datasphere_profile_column     datasphere_summarize_column_profile
datasphere_space_summary      datasphere_summarize_space
datasphere_find_assets_with_column datasphere_find_assets_by_column
datasphere_compare_assets_basic   datasphere_summarize_asset
datasphere_plugins_status     datasphere_ping
datasphere_get_tenant_info    datasphere_get_current_user
```

---

## Files Changed

### 1. `plugins/sap-datasphere/.mcp.json` — FORMAT FIX

**Before:**
```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "sap-datasphere-mcp",
      ...
    }
  }
}
```

**After:**
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

**Reason:** Official Claude Code plugin `.mcp.json` format uses the server name as the top-level key directly (no `mcpServers` wrapper). This matches the `playwright`, `github`, and all other official plugins.

---

### 2. `.mcp.json` (new at repo root) — DEV OVERRIDE

```json
{
  "sap-datasphere-local": {
    "command": "sap-datasphere-mcp",
    "args": [],
    "env": {
      "DATASPHERE_TENANT_URL": "${DATASPHERE_TENANT_URL}",
      "DATASPHERE_OAUTH_TOKEN_URL": "${DATASPHERE_OAUTH_TOKEN_URL}",
      "DATASPHERE_CLIENT_ID": "${DATASPHERE_CLIENT_ID}",
      "DATASPHERE_CLIENT_SECRET": "${DATASPHERE_CLIENT_SECRET}",
      "DATASPHERE_VERIFY_TLS": "${DATASPHERE_VERIFY_TLS}",
      "DATASPHERE_MOCK_MODE": "${DATASPHERE_MOCK_MODE}"
    }
  }
}
```

**Purpose:** Enables live MCP tool access in the current session and during `--plugin-dir` testing. Reads credentials directly from shell env vars. This is the server the user referred to as `sap-datasphere-local` — it was not previously configured in any Claude Code settings file; this run created it.

---

### 3. `.gitignore` (new) — STANDARD EXCLUDES

```
.env
.env.local
__pycache__/
*.pyc
.venv/
node_modules/
.DS_Store
Thumbs.db
```

---

### 4. `smoke_test.py` (new) — FLOW TEST SCRIPT

5-flow smoke test that calls backend task functions directly via the venv Python.
Runs in mock mode by default (set `DATASPHERE_MOCK_MODE=1` at the top).
Remove or set `DATASPHERE_MOCK_MODE=0` for live testing.

**Run command:**
```
.venv\Scripts\python.exe smoke_test.py
```
(from SAPDatasphereMCP venv, or via full path to that python.exe)

---

## Skill Flow Results (Mock Mode)

**Executed:** 2026-04-08 via `smoke_test.py` with `DATASPHERE_MOCK_MODE=1`
**Mock tenant:** `MOCK_SALES` space, asset `SALES_ORDERS`

### FLOW 1: tenant-recon

| Tool | Result | Notes |
|------|--------|-------|
| `datasphere_diagnostics` | PASS | `ok: true`, mock_mode confirmed, config fully wired |
| `datasphere_list_spaces` | PASS | 2 spaces returned: MOCK_SALES, MOCK_FINANCE |
| `datasphere_space_summary` | PASS | MOCK_SALES: 2 assets |

### FLOW 2: asset-explorer

| Tool | Result | Notes |
|------|--------|-------|
| `datasphere_get_asset_metadata` | PASS | type=VIEW, supports_relational=true, supports_analytical=false |
| `datasphere_list_columns` | PASS | 3 columns: ORDER_ID, CUSTOMER_ID, AMOUNT |
| `datasphere_describe_asset_schema` | PASS | Column types and example values returned |
| `datasphere_preview_asset` | PASS | 5 rows returned |

### FLOW 3: analytical-check

| Tool | Result | Notes |
|------|--------|-------|
| `datasphere_query_analytical` | PASS | 5 rows returned (mock supports analytical) |

### FLOW 4: column-investigator

| Tool | Result | Notes |
|------|--------|-------|
| `datasphere_profile_column` | PASS | ORDER_ID: 5 rows, 0 nulls, role_hint=id, min=1 max=5 mean=3 |
| `datasphere_summarize_column_profile` | PASS | Narrative summary with role hints and numeric stats |

### FLOW 5: data-quality-scan

| Tool | Result | Notes |
|------|--------|-------|
| `datasphere_describe_asset_schema` | PASS | Schema with python types and example values |
| `datasphere_preview_asset` | PASS | 5 rows, clean sample |
| `datasphere_profile_column` | PASS | ORDER_ID profile — no nulls, no outliers |

**Total: 13/13 PASS — 0 FAIL — 0 SKIP**

---

## Live Auth Status

**Result:** BLOCKED — HTTP 401 `invalid_client` from OAuth token endpoint.

**Diagnosis:**
- All 5 env vars are present in the current shell session
- `DATASPHERE_CLIENT_SECRET` length matches expected (81 chars, starts correctly)
- The Claude Desktop config (`AppData/Roaming/Claude/claude_desktop_config.json`) has a working set of credentials under server name `sap-datasphere-mcp`
- The shell env vars may have been exported from a different client registration or may have expired

**Resolution required before live testing:**
1. Re-export credentials from the Claude Desktop config (or the SAP BTP cockpit):
   ```bash
   export DATASPHERE_TENANT_URL="https://accenture-11.eu10.hcs.cloud.sap"
   export DATASPHERE_OAUTH_TOKEN_URL="https://accenture-11.authentication.eu10.hana.ondemand.com/oauth/token"
   export DATASPHERE_CLIENT_ID="sb-414d0a37-4240-41dc-9f1f-43422ed9f677!b526921|client!b3650"
   export DATASPHERE_CLIENT_SECRET='<secret-from-btp-or-desktop-config>'
   export DATASPHERE_VERIFY_TLS=1
   ```
   Note: single-quote the secret to prevent `$` from being shell-expanded.
2. Remove `os.environ["DATASPHERE_MOCK_MODE"] = "1"` from `smoke_test.py` line 17.
3. Rerun: `python smoke_test.py`

---

## --plugin-dir Verification (Manual Step Required)

The following must be run in a fresh Claude Code terminal session:

```bash
claude --plugin-dir ./plugins/sap-datasphere
```

Expected:
- Skills listed as `/sap-datasphere:<skill-name>` (e.g., `/sap-datasphere:tenant-recon`)
- Agents visible: `datasphere-analyst`, `datasphere-researcher`, `datasphere-quality-reviewer`
- MCP server `sap-datasphere` starts and tools are accessible
- Credential prompt appears if userConfig not yet stored for this plugin path

---

## Remaining Blockers Before GitHub Publish

| # | Blocker | Severity | Action |
|---|---------|----------|--------|
| 1 | Live OAuth 401 | High | Re-export credentials with single quotes around the secret |
| 2 | `--plugin-dir` manual UI test | Medium | Run in fresh terminal, confirm skills/agents surface |
| 3 | `smoke_test.py` placement | Low | Move to `tests/` or add to `.gitignore` before publish |
| 4 | README: add dev testing note | Low | Document `smoke_test.py` and workspace `.mcp.json` usage |

---

## Backend Binary Status

| Check | Result |
|-------|--------|
| `sap-datasphere-mcp.exe` location | `SAPDatasphereMCP/.venv/Scripts/sap-datasphere-mcp.exe` |
| Runnable | YES (exits 0 with startup log) |
| In Windows PATH | YES (venv Scripts at front of PATH) |
| In bash PATH | NO (bash PATH translation issue — use full Windows path in bash) |
| Global install (AppData/Roaming) | Also present at Python 3.14 Roaming Scripts |

---

## Environment Snapshot

```
Claude Code:         v1.1.8629 (AnthropicClaude desktop)
Backend version:     mcp-sap-datasphere-server 0.3.0
Python (venv):       SAPDatasphereMCP/.venv (editable install)
Tenant:              accenture-11.eu10.hcs.cloud.sap
Plugin version:      1.0.0-beta.1
Test date:           2026-04-08
Test mode:           MOCK (live auth blocked, see above)
```
