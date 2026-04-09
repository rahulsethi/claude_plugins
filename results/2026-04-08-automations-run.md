# Automations Implementation Run: sap-datasphere Plugin Scaffold
**Date:** 2026-04-08
**Scope:** Implement all recommended Claude Code automations — hooks, skills, subagent, and smoke_test portability fixes.

---

## Summary

| Item | Type | Status |
|------|------|--------|
| `smoke_test.py` portability fix | Script fix | DONE |
| Version consistency hook | PostToolUse hook | DONE |
| .mcp.json format guard hook | PreToolUse hook | DONE |
| `/release` skill | Developer skill | DONE |
| `/validate-plugin` skill | Developer skill | DONE |
| `release-reviewer` subagent | Subagent | DONE |
| `.claude/settings.json` wired | Config update | DONE |

---

## Files Created or Modified

### 1. `smoke_test.py` — MODIFIED

**Two portability fixes applied:**

**Fix A — Mock mode default (line 15–17 before, replaced):**

Before:
```python
# Force mock mode so all 5 flows run without requiring live OAuth credentials.
# Remove this line (or set to "0") to test against the live tenant.
os.environ["DATASPHERE_MOCK_MODE"] = "1"
```

After:
```python
# Default to mock mode unless already set.
# To test against a live tenant: set DATASPHERE_MOCK_MODE=0 before running.
if "DATASPHERE_MOCK_MODE" not in os.environ:
    os.environ["DATASPHERE_MOCK_MODE"] = "1"
```

Effect: `DATASPHERE_MOCK_MODE=0 python smoke_test.py` now works for live testing without editing the file.

**Fix B — Hardcoded path removed (lines 19–25 before, replaced):**

Before:
```python
sys.path.insert(
    0,
    r"C:\Users\r.b.sethi\Documents\Projects Dev\SAP Datasphere\SAPDatasphereMCP\src",
)
```

After:
```python
import importlib.util as _ilu
_spec = _ilu.find_spec("sap_datasphere_mcp")
if _spec is None:
    sys.exit(
        "ERROR: sap_datasphere_mcp not importable.\n"
        "Activate the SAPDatasphereMCP venv or run:\n"
        "  pip install mcp-sap-datasphere-server"
    )
```

Effect: Works on any machine where the venv is active or the package is installed. No username or path assumptions.

---

### 2. `.claude/hooks/check-versions.py` — CREATED

**Type:** PostToolUse hook script
**Triggers on:** Any Edit or Write tool call that targets `plugin.json` or `marketplace.json`
**Behavior:** Reads both manifest files and compares versions. Exits 1 (error surfaced in Claude Code) if they differ. Silent no-op for all other file edits.

**Key logic:**
```python
if plugin_ver != market_ver:
    print(f"[VERSION MISMATCH] plugin.json={plugin_ver}  marketplace.json={market_ver}")
    sys.exit(1)
```

---

### 3. `.claude/hooks/guard-mcp-json.py` — CREATED

**Type:** PreToolUse hook script
**Triggers on:** Any Edit or Write targeting `plugins/sap-datasphere/.mcp.json`
**Behavior:** Prints a reminder about the correct flat format (no `mcpServers` wrapper). Exits 0 — advisory only, does not block the edit.

**Why:** The `mcpServers` wrapper regression is silent — `claude plugin validate` passes even with it, and the server just fails to start at runtime.

---

### 4. `.claude/settings.json` — MODIFIED

Added `hooks` section wiring both scripts to their respective events:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/check-versions.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/guard-mcp-json.py"
          }
        ]
      }
    ]
  },
  "enabledPlugins": {
    "claude-md-management@claude-plugins-official": true
  }
}
```

The `python` command resolves from PATH. With the SAPDatasphereMCP venv active (or any Python 3 in PATH), this works — both hook scripts use stdlib only (`json`, `sys`, `os`).

---

### 5. `.claude/skills/release/SKILL.md` — CREATED

**Invocation:** `/release` inside a Claude Code session
**What it does:**
1. Asks for new version number and change summary
2. Bumps `plugin.json` version
3. Bumps `marketplace.json` version
4. Prepends CHANGELOG entry with date
5. Prints the exact 5-step validation sequence to run next

**Why:** Replaces 5 manual, error-prone release steps with a single slash command. Prevents version drift between the two manifest files.

---

### 6. `.claude/skills/validate-plugin/SKILL.md` — CREATED

**Invocation:** `/validate-plugin` inside a Claude Code session
**What it does:**
Runs 5 checks in sequence and prints a pass/fail table:
1. `claude plugin validate .`
2. `claude plugin validate ./plugins/sap-datasphere`
3. `python smoke_test.py` — expects 13/13 PASS
4. Version consistency check (plugin.json vs marketplace.json)
5. `.mcp.json` format guard (no `mcpServers` wrapper)

**Why:** Replaces the scattered validation commands in CLAUDE.md and scaffold-usage.md with a single entry point.

---

### 7. `.claude/agents/release-reviewer.md` — CREATED

**Model:** haiku (read-only, low cost)
**Disallowed tools:** Write, Edit, Bash
**What it does:** 8-point pre-publish quality gate:
1. Version consistency (plugin.json vs marketplace.json)
2. CHANGELOG has entry for current version
3. README version reference is not stale
4. Skill count matches README
5. Agent count matches README
6. All `datasphere_*` tool names are in the v0.3.0 surface
7. No DevAssist bleed in settings.json
8. .mcp.json has no `mcpServers` wrapper

**Why:** Runs independently before GitHub publish to catch drift that accumulates across editing sessions.

---

## New Directory Structure Under `.claude/`

```
.claude/
├── settings.json          (updated — hooks wired)
├── hooks/
│   ├── check-versions.py  (new — PostToolUse version guard)
│   └── guard-mcp-json.py  (new — PreToolUse format reminder)
├── skills/
│   ├── release/
│   │   └── SKILL.md       (new — /release slash command)
│   └── validate-plugin/
│       └── SKILL.md       (new — /validate-plugin slash command)
└── agents/
    └── release-reviewer.md (new — pre-publish quality gate)
```

---

## How to Use

### Daily dev flow
No action needed. Hooks fire automatically on every Edit/Write:
- Editing `plugin.json` or `marketplace.json` → version check fires
- Editing `plugins/sap-datasphere/.mcp.json` → format reminder fires

### Before any release
```
/validate-plugin
```
Fix anything that fails, then:
```
/release
```
Follow the printed validation sequence.

### Before GitHub publish
```
Use the release-reviewer agent
```
Or: invoke it via the Agent tool. It reads all manifests and flags any blockers.

---

## Notes

- Hook scripts use stdlib only — no package dependencies.
- `python` in hook commands resolves from PATH. The SAPDatasphereMCP venv must be active (or `python` points to any Python 3).
- The `guard-mcp-json.py` hook exits 0 (advisory) — it does not block edits.
- The `check-versions.py` hook exits 1 on mismatch — Claude Code surfaces this as an error after the edit.
- GitHub MCP not yet installed — add it after `git init` and first push.
