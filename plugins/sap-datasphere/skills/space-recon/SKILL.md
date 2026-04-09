---
name: space-recon
description: Summarize a Datasphere space and suggest the best starting assets. Use when the user already named a space or wants a space-level overview.
---
<!-- File: plugins/sap-datasphere/skills/space-recon/SKILL.md -->
<!-- Version: v1 -->

Default sequence:
1. Confirm or infer the target space from recent context.
2. Run `datasphere_list_assets` for the space.
3. Run `datasphere_summarize_space` if available; otherwise use `datasphere_space_summary`.
4. Highlight 2 to 3 candidate assets worth exploring next.

Return:
- total assets
- top asset types
- sample core assets
- a next-step recommendation
