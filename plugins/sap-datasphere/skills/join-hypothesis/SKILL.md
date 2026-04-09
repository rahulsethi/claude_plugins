---
name: join-hypothesis
description: Find shared columns across assets and suggest likely joins. Use when the user asks how assets relate or where a business key appears.
---
<!-- File: plugins/sap-datasphere/skills/join-hypothesis/SKILL.md -->
<!-- Version: v1 -->

Sequence:
1. Use `datasphere_find_assets_with_column` or `datasphere_find_assets_by_column`.
2. Inspect metadata for the most likely matching assets.
3. If two strong candidates exist, run `datasphere_compare_assets_basic`.
4. Suggest the most plausible primary asset and lookup assets.

Do not claim join correctness with certainty unless the evidence is strong.
