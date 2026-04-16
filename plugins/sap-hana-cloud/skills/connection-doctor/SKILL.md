---
name: connection-doctor
description: Diagnose HANA connection problems for the plugin. Use when the MCP server starts but the database connection fails or tool results look suspicious.
---

Checklist:
1. Confirm the plugin is enabled and the HANA MCP tools are present.
2. Run `hana_test_connection`.
3. Run `hana_show_config` and confirm host, port, schema, SSL, and connection type look correct.
4. If needed, run `hana_show_env_vars` to spot missing or blank values.
5. Explain the failure class clearly: plugin load, CLI missing, network reachability, bad credentials, MDC mismatch, or certificate settings.
Guardrails:
- Prefer explicit remediation steps over generic advice.
- Do not expose secrets from masked config output.
