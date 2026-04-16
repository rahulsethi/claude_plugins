# Contributing — claude_plugins Marketplace

## Repository layout

```
claude_plugins/
├── .claude-plugin/
│   └── marketplace.json          marketplace manifest (plugin registry)
├── plugins/
│   ├── sap-datasphere/           SAP Datasphere plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       plugin manifest (name, version, userConfig)
│   │   ├── .mcp.json             MCP server launcher — uses ${user_config.*}
│   │   ├── skills/               skill directories, each with a SKILL.md
│   │   ├── agents/               agent markdown files
│   │   ├── CLAUDE.md             plugin-level working rules for Claude sessions
│   │   ├── CHANGELOG.md
│   │   └── README.md
│   └── sap-hana-cloud/           SAP HANA Cloud plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .mcp.json
│       ├── skills/
│       ├── agents/
│       ├── hooks/
│       │   └── hooks.json        plugin-level PreToolUse write guard
│       ├── scripts/
│       │   ├── hana_sql_guard.py           write guard logic
│       │   └── project_plugin_validate_reminder.py  dev reminder hook
│       ├── examples/             worked example SQL and Python files
│       ├── CLAUDE.md
│       ├── CHANGELOG.md
│       └── README.md
├── .mcp.json                     dev-only MCP launcher (uses shell env vars)
├── CLAUDE.md                     repo-level working rules
├── smoke_test.py                 mock-mode smoke test for sap-datasphere
└── docs/                         installation and reference guides
```

---

## Plugin quick-reference

| Plugin | Backend package | Backend language | Write support | Hook |
|--------|----------------|-----------------|---------------|------|
| `sap-datasphere` | `mcp-sap-datasphere-server` (pip) | Python | None (read-only) | None |
| `sap-hana-cloud` | `hana-mcp-server` (npm, via npx) | Node.js | Reviewed DDL/DML | PreToolUse write guard |

---

## Adding a new plugin

1. Create `plugins/<your-plugin>/` following the structure above.
2. Add `.claude-plugin/plugin.json` — required fields: `name`, `version`, `description`, `author`.
3. Wire credentials via `userConfig` in `plugin.json` and `${user_config.*}` in `.mcp.json`.
4. Register the plugin in `.claude-plugin/marketplace.json` under `plugins`.
5. Validate: `claude plugin validate ./plugins/<your-plugin>`
6. Add a row to the `docs/installation.md` prerequisite table.
7. Run `/release` to bump versions and update the CHANGELOG.

---

## Key constraints

### plugin.json
- Must live in `.claude-plugin/` inside the plugin directory.
- Required fields: `name`, `version`, `description`, `author`.
- Every `userConfig` field requires `title` (string) and `type` (`string|number|boolean|directory|file`).
- Sensitive fields (secrets, passwords, tokens) must have `"sensitive": true`.
- Use `type: "string"` for fields the backend reads as env vars and compares as strings (e.g. `"1"`/`"0"`).

### .mcp.json
- Must use the server name as the top-level key — **no `mcpServers` wrapper**.
  - Correct: `{ "sap-hana-cloud": { "command": "npx", "env": {...} } }`
  - Wrong: `{ "mcpServers": { "sap-hana-cloud": {...} } }`
- Use `${user_config.*}` substitutions for all credential-derived env vars.
- The root `.mcp.json` is dev-only (reads from shell env vars). Plugin `.mcp.json` files use `${user_config.*}`.

### Skills
- End-user skills belong in `plugins/<name>/skills/`.
- Developer tools (`/release`, `/validate-plugin`) belong in `.claude/skills/`.
- Never mix them.

### Hooks
- Plugin-level hooks live in `plugins/<name>/hooks/hooks.json`.
- Use `${CLAUDE_PLUGIN_ROOT}` to reference scripts inside the plugin directory.
- Use `python` (not `python3`) for cross-platform Windows/Unix compatibility.
- Hook commands run in the project root, not the plugin directory.

---

## Dev setup — sap-datasphere (local testing)

```bash
# Install the backend CLI first
pip install mcp-sap-datasphere-server

# Export credentials as shell env vars (single-quotes prevent $ expansion on secrets)
export DATASPHERE_TENANT_URL='https://your-tenant.eu10.hcs.cloud.sap'
export DATASPHERE_OAUTH_TOKEN_URL='https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token'
export DATASPHERE_CLIENT_ID='your-client-id'
export DATASPHERE_CLIENT_SECRET='your$secret'
export DATASPHERE_VERIFY_TLS='1'
export DATASPHERE_MOCK_MODE='0'

# Launch Claude with the plugin
claude --plugin-dir ./plugins/sap-datasphere
```

For mock-mode testing without a live tenant:

```bash
export DATASPHERE_MOCK_MODE='1'
claude --plugin-dir ./plugins/sap-datasphere
# Then inside Claude Code:
# /sap-datasphere:mock-mode-demo
```

## Dev setup — sap-hana-cloud (local testing)

```bash
# Node.js 18+ is required for npx hana-mcp-server
node --version

# Export credentials
export HANA_HOST='your-host.hanacloud.ondemand.com'
export HANA_PORT='443'
export HANA_USER='CLAUDE_USER'
export HANA_PASSWORD='your$password'
export HANA_SCHEMA='YOUR_SCHEMA'
export HANA_SSL='true'
export HANA_ENCRYPT='true'
export HANA_VALIDATE_CERT='true'

# Optional — set write mode and work schema
export HANA_WRITE_MODE='ask'
export HANA_WORK_SCHEMA='ML_WORK'

# Launch Claude with the plugin
claude --plugin-dir ./plugins/sap-hana-cloud
```

---

## Validation

```bash
# Validate the marketplace manifest
claude plugin validate .

# Validate individual plugins
claude plugin validate ./plugins/sap-datasphere
claude plugin validate ./plugins/sap-hana-cloud
```

Both should exit 0 with `✔ Validation passed`.

Run the built-in validate skill inside Claude Code for a full sequence including smoke test:

```
/validate-plugin
```

---

## Release flow

1. Run `/release` inside a Claude Code session — handles version bumps in `plugin.json` and `marketplace.json`, and prepends the CHANGELOG entry.
2. Run `release-reviewer` agent for a pre-publish quality gate.
3. For `sap-hana-cloud`, also run `/sap-hana-cloud:release-smoke-test` to verify the full 6-stage sequence including the write guard.

---

## Write guard — sap-hana-cloud

The write guard in `plugins/sap-hana-cloud/scripts/hana_sql_guard.py` is the most critical component of the HANA plugin. After any change to this file or to `hooks/hooks.json`, verify the guard by running all five sub-tests in the `release-smoke-test` skill:

- 5a: SELECT passes through without a hook prompt
- 5b: CREATE TABLE triggers a confirmation prompt
- 5c: DROP TABLE is hard-blocked (no prompt)
- 5d: DELETE without WHERE is hard-blocked (no prompt)
- 5e: Multi-statement SQL is hard-blocked (no prompt)

A write guard regression (prompt appearing instead of hard-block, or silent pass-through) is the highest-severity issue this plugin can ship with.

---

## Keeping docs in sync

After any structural change (new skill, new agent, version bump, new config field), update:

1. The plugin's `README.md`
2. The relevant guide in `docs/` (`sap-datasphere.md` or `sap-hana-cloud.md`)
3. The root `README.md` if the plugin's skill/agent count changes
4. `CHANGELOG.md` in the plugin directory

Run `/release` to handle version bumps automatically.
