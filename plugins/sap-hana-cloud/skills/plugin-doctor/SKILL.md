---
name: plugin-doctor
description: Diagnose plugin packaging, marketplace, or hook problems for sap-hana-cloud. Use when commands are missing, hooks do not fire, or validation fails.
---

Sequence:
1. Confirm the plugin is enabled and visible in `/plugin` or `/help`.
2. Confirm `claude plugin validate ./plugins/sap-hana-cloud` was run.
3. Check `.claude-plugin/plugin.json`, `.mcp.json`, and `hooks/hooks.json` for naming or schema mismatches.
4. If the HANA tools exist, run `hana_show_config` to verify the server started.
5. If write review behavior is wrong, inspect `scripts/hana_sql_guard.py` and remind the user to re-test it.
Return a short diagnosis and the next exact fix.
