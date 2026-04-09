---
name: validate-plugin
description: Run the full plugin validation sequence and report pass/fail for each check. Use before any release or after any structural change to plugin.json, .mcp.json, or skill/agent files.
---

Run each check below in order using the Bash tool. Report pass or fail per step. Stop and explain any failure before moving on.

**Check 1 — Structural validation (marketplace root)**
```bash
claude plugin validate .
```
Expected: exit code 0. Any non-zero exit is a FAIL.

**Check 2 — Structural validation (plugin directory)**
```bash
claude plugin validate ./plugins/sap-datasphere
```
Expected: exit code 0.

**Check 3 — Smoke test (mock mode)**
```bash
python smoke_test.py
```
Expected output contains: `Total: 13 PASS  0 FAIL  0 SKIP`
If DATASPHERE_MOCK_MODE is not set it defaults to mock automatically.

**Check 4 — Version consistency**
Read both manifest files and compare versions:
- `plugins/sap-datasphere/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

They must match. If they differ, report the mismatch and stop.

**Check 5 — .mcp.json format guard**
Read `plugins/sap-datasphere/.mcp.json`.
Confirm the file does NOT contain a top-level `mcpServers` key.
The server name (`sap-datasphere`) must be the top-level key directly.

Print a summary table when all checks are done:

| Check | Result |
|-------|--------|
| plugin validate (root) | PASS / FAIL |
| plugin validate (plugin dir) | PASS / FAIL |
| smoke_test.py | X/13 PASS |
| Version consistency | MATCH / MISMATCH |
| .mcp.json format | OK / REGRESSION |

If all checks pass, tell the user they can proceed to `claude --plugin-dir` testing.
If any check fails, stop and explain what to fix.
