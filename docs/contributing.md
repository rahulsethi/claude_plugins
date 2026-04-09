# Contributing — claude_plugins Marketplace

## Repository layout

```
claude_plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest (name, plugin list)
├── plugins/
│   └── sap-datasphere/           # One directory per plugin
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest (name, version, userConfig)
│       ├── .mcp.json             # MCP server launcher — uses ${user_config.*}
│       ├── skills/               # Skill directories, each with a SKILL.md
│       ├── agents/               # Agent markdown files
│       ├── CLAUDE.md             # Plugin-level working rules for Claude sessions
│       ├── CHANGELOG.md
│       └── README.md
├── .mcp.json                     # Dev-only MCP launcher (uses shell env vars)
├── CLAUDE.md                     # Repo-level working rules
└── docs/                         # This folder
```

## Adding a new plugin

1. Create `plugins/<your-plugin>/` with the structure above.
2. Add a `plugin.json` manifest — required fields: `name`, `version`, `description`, `author`.
3. Wire credentials via `userConfig` in `plugin.json` and `${user_config.*}` in `.mcp.json`.
4. Register the plugin in `.claude-plugin/marketplace.json` under `plugins`.
5. Validate: `claude plugin validate ./plugins/<your-plugin>`
6. Run `/release` to bump versions and update the CHANGELOG.

## Key constraints

- `plugin.json` lives in `.claude-plugin/` inside the plugin directory.
- `.mcp.json` must use the server name as the top-level key — no `mcpServers` wrapper.
- Each `userConfig` field requires `title` (string) and `type` (`string|number|boolean|directory|file`).
- Sensitive fields (secrets, tokens) must have `"sensitive": true`.
- Use `type: "string"` for fields that the backend reads as env vars and compares to `"1"`/`"0"`.
- End-user skills belong in `plugins/<name>/skills/`. Developer tools belong in `.claude/skills/`.

## Dev setup (local testing)

```bash
# Export credentials as shell env vars (single-quotes prevent $ expansion)
export DATASPHERE_TENANT_URL='https://...'
export DATASPHERE_CLIENT_SECRET='your$secret'

# Launch Claude pointing at the plugin
claude --plugin-dir ./plugins/sap-datasphere
```

## Validation

```bash
claude plugin validate .                          # marketplace manifest
claude plugin validate ./plugins/sap-datasphere  # plugin manifest
```

Both should exit 0.

## Release flow

Run `/release` inside a Claude Code session — handles version bumps in `plugin.json` and `marketplace.json`, and prepends the CHANGELOG entry.

Run `release-reviewer` agent for a pre-publish quality gate before pushing.
