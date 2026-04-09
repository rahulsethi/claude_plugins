<!-- File: docs/official-and-community-plugin-recommendations.md -->
<!-- Version: v1 -->

# Official and Community Plugin Recommendations

## Install first for this SAP Datasphere wrapper project

### Official marketplace plugins

Install these first:

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin install github@claude-plugins-official
/plugin install commit-commands@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install pyright-lsp@claude-plugins-official
```

### Why these are high leverage

- `github` — useful for issues, releases, and repo inspection.
- `commit-commands` — reduces friction during small, frequent commit cycles.
- `claude-code-setup` — helpful for scanning a new repo and suggesting automations.
- `claude-md-management` — useful for keeping `CLAUDE.md` lean and current.
- `pyright-lsp` — strong fit for the Python MCP backend.

### Prerequisite for `pyright-lsp`

Install the Pyright binary first:

```bash
npm install -g pyright
```

or:

```bash
pipx install pyright
```

## Official plugins that are useful later

```text
/plugin install feature-dev@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
```

- `feature-dev` is good when you want Claude to follow a more deliberate feature-building sequence.
- `frontend-design` is especially useful later for website work or polished UI tasks.

## Community tools worth knowing about

### 1. oh-my-claudecode

Use it when you want heavier orchestration, team workflows, or opinionated automation.
Use it **after** the baseline plugin works, not before.

### 2. playwright-skill

Very useful when you need browser automation, smoke tests, screenshots, or QA of web flows.
This is one of the best community add-ons for website and web-app verification.

### 3. claude-mem

Interesting for aggressive context capture and cross-session recall.
Use carefully because it adds more moving parts and may be too heavy for a simple wrapper plugin workflow.

### 4. ccusage and related usage analyzers

Not a plugin-first choice, but very useful for understanding session cost, model mix, and token burn.
Good for personal optimization and team reporting.

## Community marketplaces to browse, not blindly install from

- `claude-market/marketplace`
- `kivilaid/plugin-marketplace`
- `gpambrozio/ClaudeCodePlugins`
- `ccplugins/awesome-claude-code-plugins`

Use them as discovery sources and then install selectively.

## Suggested install order for this project

1. official marketplace plugins listed above
2. your local `sap-datasphere` wrapper plugin
3. optionally `playwright-skill` if you want browser-based smoke tests later
4. optionally `oh-my-claudecode` only after the base workflow is stable

## Recommendation summary

For this project, keep it simple:

- yes to official workflow and LSP plugins
- yes to your own wrapper plugin
- maybe to Playwright later
- maybe to OMC later
- no to large community bundles on day 1
