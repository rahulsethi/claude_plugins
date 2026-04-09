---
name: release-smoke-test
description: Run a manual release smoke test for the plugin and backend integration. Use before publishing or after structural edits.
---
<!-- File: plugins/sap-datasphere/skills/release-smoke-test/SKILL.md -->
<!-- Version: v1 -->

Run this sequence manually:
1. `datasphere_diagnostics`
2. `datasphere_list_spaces`
3. `datasphere_search_assets`
4. `datasphere_get_asset_metadata`
5. `datasphere_list_columns`
6. `datasphere_preview_asset`
7. `datasphere_profile_column`
8. `datasphere_query_analytical` if supported

Report pass or fail per step and call out any regression clearly.
