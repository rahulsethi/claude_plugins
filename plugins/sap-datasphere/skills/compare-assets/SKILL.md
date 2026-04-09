---
name: compare-assets
description: Compare two assets to see whether they represent the same entity or related grains. Use when the user wants a quick structural comparison.
---
<!-- File: plugins/sap-datasphere/skills/compare-assets/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Run `datasphere_compare_assets_basic`.
2. If needed, pull `datasphere_summarize_asset` for both sides.
3. Highlight common columns, mismatches, possible join keys, and likely grain differences.
