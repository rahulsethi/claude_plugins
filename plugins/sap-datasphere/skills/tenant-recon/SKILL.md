---
name: tenant-recon
description: Run diagnostics, list spaces, and summarize one promising space. Use when the user asks what is available in the tenant or wants orientation.
---
<!-- File: plugins/sap-datasphere/skills/tenant-recon/SKILL.md -->
<!-- Version: v1 -->

Work in this order:
1. Run `datasphere_diagnostics`.
2. If diagnostics fail, explain the failure clearly and stop.
3. Run `datasphere_list_spaces`.
4. Pick one promising space and run `datasphere_summarize_space` or `datasphere_space_summary`.
5. Return a short orientation note: tenant health, number of spaces, recommended starting space, and next best action.

Guardrails:
- Prefer a concise summary.
- If the environment is in mock mode, say so explicitly.
- Do not guess spaces or tenant details that were not returned by the tools.
