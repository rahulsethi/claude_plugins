<!-- File: plugins/sap-datasphere/CLAUDE.md -->
<!-- Version: v2 -->

# sap-datasphere Plugin Rules

## Purpose
This plugin wraps the existing SAP Datasphere MCP server for Claude Code.

## Boundaries
- Do not copy backend Python code into this plugin.
- Do not add write or admin functionality.
- Keep the plugin focused on setup, orchestration, and user workflows.
- Keep skill wording aligned with the current Datasphere v0.3 tool surface.
- `.mcp.json` must use the server name as the top-level key directly — NO `mcpServers` wrapper.
  Correct: `{ "sap-datasphere": { "command": "...", "env": {...} } }`
  Wrong:   `{ "mcpServers": { "sap-datasphere": {...} } }`
- Env vars in plugin `.mcp.json` must use `${user_config.*}` template syntax (not shell env vars).
- Each `userConfig` field in `plugin.json` requires `title` (string) and `type` (`string|number|boolean|directory|file`) — validator errors without them.
- Use `type: "string"` for `verify_tls` and `mock_mode` even though they hold `"1"`/`"0"` — the MCP server compares them as strings, not booleans.
- End-user Datasphere skills belong in `skills/` here. Developer tools (/release, /validate-plugin) belong in `.claude/skills/` at repo root — never mix them.

## Current state (1.0.0-beta.2)
- Skills: 20 across 6 categories (orientation, exploration, querying, quality, advanced, utilities)
- Agents: 5 (datasphere-analyst, datasphere-researcher, datasphere-quality-reviewer,
           datasphere-query-assistant, datasphere-data-steward)

## Skill design rules
- Skills should orchestrate existing MCP tools.
- Keep instructions operational and deterministic.
- Prefer step sequences over long prose.
- Mention graceful fallback behavior when a tool is unavailable.

## Agent design rules
- Prefer subagents over agent teams.
- Use `haiku` only for cheap discovery-style roles.
- Use `sonnet` for main analysis roles.
- Keep reviewer agents read-only by default.

## Validation
- `/validate-plugin` — full check sequence (preferred)
- `claude plugin validate .` and `claude plugin validate ./plugins/sap-datasphere`
- Test manually: `/sap-datasphere:tenant-recon`, `/sap-datasphere:cross-space-search`, `/sap-datasphere:query-builder`

## Release checklist
- Run `/release` — handles version bump (plugin.json + marketplace.json) and CHANGELOG entry
- Re-run local plugin-dir test and marketplace install test manually
- Run `release-reviewer` agent for final pre-publish gate
