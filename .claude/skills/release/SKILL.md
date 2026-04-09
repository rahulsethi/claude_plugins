---
name: release
description: Run the full plugin release checklist. Bumps version in plugin.json and marketplace.json, prepends a CHANGELOG entry, and prints the exact validation commands to run next.
---

Ask the user for:
1. The new version number (e.g. `1.0.0-beta.2`)
2. A one-line summary of what changed in this release

Then execute these steps in order:

**Step 1 — Bump plugin.json**
Read `plugins/sap-datasphere/.claude-plugin/plugin.json`.
Update the `version` field to the new version. Write the file back.

**Step 2 — Bump marketplace.json**
Read `.claude-plugin/marketplace.json`.
Update `plugins[0].version` to match the new version. Write the file back.

**Step 3 — Prepend CHANGELOG entry**
Read `plugins/sap-datasphere/CHANGELOG.md`.
Prepend a new entry at the very top (above any existing entries):

```
## [<version>] — <today's date YYYY-MM-DD>
### Changed
- <summary provided by user>
```

Write the file back.

**Step 4 — Confirm**
Print a short confirmation:
```
Release <version> prepared.
Files updated:
  plugins/sap-datasphere/.claude-plugin/plugin.json
  .claude-plugin/marketplace.json
  plugins/sap-datasphere/CHANGELOG.md
```

**Step 5 — Print validation sequence**
Print the exact commands the user must run next (do NOT run them yourself):

```
# 1. Structural validation
claude plugin validate .
claude plugin validate ./plugins/sap-datasphere

# 2. Smoke test (mock mode)
python smoke_test.py

# 3. Local plugin-dir test (fresh terminal required)
claude --plugin-dir ./plugins/sap-datasphere

# 4. Marketplace install test (inside a Claude Code session)
/plugin marketplace add ./<path-to-this-repo>
/plugin install sap-datasphere@rahulsethi
/reload-plugins
```

Remind the user to test local plugin-dir mode BEFORE marketplace mode.
