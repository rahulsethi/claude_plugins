---
name: asset-card
description: Create a concise semantic card for a chosen asset. Use when the user wants a short reusable summary instead of a raw inspection.
---
<!-- File: plugins/sap-datasphere/skills/asset-card/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Use `datasphere_summarize_asset` if available.
2. Fill gaps with metadata, columns, preview, and profile data.
3. Return a compact asset card with purpose, keys, measures, dimensions, query paths, and caveats.
