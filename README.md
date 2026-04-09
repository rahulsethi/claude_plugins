<!-- File: README.md -->
<!-- Version: v1 -->

# SAP Datasphere Claude Code Marketplace Scaffold

This scaffold gives you a **separate Claude Code marketplace repo** that wraps the existing
**SAP Datasphere MCP server** instead of reimplementing it.

## What this scaffold includes

- A root marketplace manifest under `.claude-plugin/marketplace.json`
- A thin `sap-datasphere` Claude Code plugin under `plugins/sap-datasphere/`
- `CLAUDE.md` files for both the marketplace repo and the plugin package
- A `.mcp.json` that launches the existing `sap-datasphere-mcp` CLI
- Datasphere-focused skills and subagents aligned to the current v0.3 tool surface
- Documentation for local testing, publishing, and Claude Code optimization
- Separate notes on official and community plugins worth installing

## Repository layout

```text
sap-datasphere-claude-marketplace-scaffold/
├── .claude-plugin/
│   └── marketplace.json
├── CLAUDE.md
├── README.md
├── docs/
│   ├── claude-code-optimization.md
│   ├── examples/
│   │   ├── home-CLAUDE.example.md
│   │   └── project-CLAUDE.local.example.md
│   ├── official-and-community-plugin-recommendations.md
│   └── scaffold-usage.md
└── plugins/
    └── sap-datasphere/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── .mcp.json
        ├── agents/
        ├── skills/
        ├── CHANGELOG.md
        ├── CLAUDE.md
        └── README.md
```

## Design choices locked in here

1. This is a **wrapper plugin**, not a second Datasphere backend.
2. The plugin expects the existing MCP package/CLI to already be installable on the machine.
3. The plugin uses Claude Code `userConfig` to collect Datasphere connection values and exports them into the MCP server environment.
4. The initial plugin stays read-only and maps directly to your current v0.3 server surface.
5. The skill catalog is intentionally oriented around real user workflows instead of one-tool-at-a-time commands.

## First-run sequence

1. Install and verify the existing backend server.
2. Validate this marketplace scaffold.
3. Test the plugin locally with `--plugin-dir`.
4. Add the marketplace locally.
5. Install the `sap-datasphere` plugin from the local marketplace.
6. Run the smoke-test skills.

See `docs/scaffold-usage.md` for the exact command sequence.

## What you should edit before publishing

- Marketplace repository URL
- Plugin repository URL
- Plugin author metadata
- Plugin descriptions and README copy
- Final skill wording once you test with your real tenant
- Version numbers once you are ready to ship
