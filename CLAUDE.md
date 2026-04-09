<!-- File: CLAUDE.md -->
<!-- Version: v2 -->

# Marketplace Repo Working Rules

## Mission
Build and ship a thin Claude Code marketplace and plugin wrapper around the existing SAP Datasphere MCP server.

## Source of truth
- Backend server repo: keep it separate from this repo.
- Backend package: `mcp-sap-datasphere-server`
- Backend CLI: `sap-datasphere-mcp`

## Hard boundaries
- Do not reimplement Datasphere client logic here.
- Do not add write or admin actions.
- Do not mix DevAssist or Sethi work into this wrapper repo.

## Repo structure
- `.claude-plugin/marketplace.json` — marketplace manifest
- `.mcp.json` — dev-only local server (reads `DATASPHERE_*` shell env vars)
- `.claude/settings.json` — project hooks (version check + .mcp.json guard)
- `.claude/skills/` — developer skills: `/release`, `/validate-plugin`
- `.claude/agents/` — developer agent: `release-reviewer`
- `.claude/hooks/` — hook scripts: `check-versions.py`, `guard-mcp-json.py`
- `plugins/sap-datasphere/` — the installable plugin

## Environment notes
- Bash shell in this env has no Unix utils — use Glob/Grep/Read tools instead of ls/find/grep/cat.
- `claude plugin validate` outputs `✔ Validation passed` on success (exit 0). Warnings are non-blocking; errors fail with exit 1.
- `DATASPHERE_CLIENT_SECRET` contains `$` — always export with single quotes to prevent shell expansion.
- Python scripts writing to this terminal: ASCII only (Windows cp1252; box-drawing chars throw UnicodeEncodeError).

## Working style
- Explore first, then plan, then edit.
- Make one logical change set at a time.
- Validate after every change set.
- Keep `CLAUDE.md` concise and move repeatable workflows into skills.
- Keep plugin components at plugin root. Only `plugin.json` belongs in `.claude-plugin/`.

## Validation commands
- `/validate-plugin` — runs all checks in sequence (preferred)
- `claude plugin validate .`
- `claude plugin validate ./plugins/sap-datasphere`
- `python smoke_test.py` — 13-tool mock-mode smoke test (set `DATASPHERE_MOCK_MODE=0` for live)
- `claude --plugin-dir ./plugins/sap-datasphere`
- `/reload-plugins`
- `/plugin marketplace add ./<path-to-this-repo>`
- `/plugin install sap-datasphere@sethir-marketplace`

## Release rules
- Run `/release` to bump versions, update CHANGELOG, and get the validation sequence.
- Use the `release-reviewer` agent for a pre-publish quality gate before GitHub push.
- Test local plugin-dir mode before marketplace mode.
- Test marketplace mode before public distribution.

## Session outputs
- Document significant session results in `results/YYYY-MM-DD-<topic>.md` (validation runs, migrations, audits).

## Repo boundaries
- Root README explains marketplace-level usage.
- Plugin README explains plugin installation, configuration, and skill entrypoints.
- Docs folder holds optimization notes and plugin recommendations.
