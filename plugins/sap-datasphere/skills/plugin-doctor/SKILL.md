---
name: plugin-doctor
description: Diagnose setup problems with the SAP Datasphere wrapper plugin. Use when the MCP server does not appear, credentials fail, or tools are missing.
---
<!-- File: plugins/sap-datasphere/skills/plugin-doctor/SKILL.md -->
<!-- Version: v1 -->

Checklist:
1. Confirm the plugin is enabled.
2. Confirm `sap-datasphere-mcp` exists in PATH.
3. Confirm plugin userConfig values were supplied.
4. Run `datasphere_diagnostics` if the server started.
5. Explain the likely failure class: plugin load, CLI missing, config missing, auth failure, or tenant access problem.

Prefer explicit remediation steps over generic troubleshooting advice.
