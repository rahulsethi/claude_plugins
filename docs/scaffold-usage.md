<!-- File: docs/scaffold-usage.md -->
<!-- Version: v1 -->

# Scaffold Usage

## 1. Validate the existing backend server first

Run these commands in the existing `SAPDatasphereMCP` repo before touching the plugin scaffold:

```bash
python -m venv .venv
# activate your virtualenv
pip install -e ".[dev]"
pytest
python demo_mcp_list_spaces.py
python demo_mcp_list_assets.py
python demo_mcp_preview_filtered.py
python demo_mcp_describe_asset.py
python demo_mcp_query_relational.py
python demo_mcp_search_assets.py
python demo_mcp_space_summary.py
python demo_mcp_profile_column.py
```

Then confirm the CLI is available:

```bash
sap-datasphere-mcp
```

## 2. Install the backend package on the machine that will run Claude Code

Choose one path:

```bash
pip install mcp-sap-datasphere-server
```

or:

```bash
pipx install mcp-sap-datasphere-server
```

## 3. Validate this marketplace scaffold

From the root of this scaffold repo:

```bash
claude plugin validate .
```

## 4. Test the plugin directly without installing it

```bash
claude --plugin-dir ./plugins/sap-datasphere
```

Inside Claude Code:

```text
/reload-plugins
/help
/agents
```

Try these namespaced skill calls:

```text
/sap-datasphere:tenant-recon
/sap-datasphere:asset-explorer
/sap-datasphere:analytical-check
```

## 5. Add the marketplace locally and install from it

Inside Claude Code:

```text
/plugin marketplace add ./<path-to-this-repo>
/plugin install sap-datasphere@sethir-marketplace
/reload-plugins
```

## 6. Provide configuration when the plugin prompts for it

The plugin manifest asks Claude Code for:

- tenant URL
- OAuth token URL
- client ID
- client secret
- verify TLS flag
- mock mode flag

Those values are injected into the MCP server environment automatically.

## 7. Recommended smoke test flow

Run these in Claude Code after install:

1. `Run datasphere diagnostics and tell me whether we are in live or mock mode.`
2. `List spaces and summarize the most interesting one.`
3. `Find an asset related to employee or sales and show metadata plus columns.`
4. `Preview rows and profile one likely ID column and one likely measure column.`
5. `If the asset supports analytical queries, run a small analytical query.`

## 8. Publish path once local testing works

- Push the repo to GitHub.
- Add the marketplace from GitHub:

```text
/plugin marketplace add <owner>/<repo>
/plugin install sap-datasphere@sethir-marketplace
```

- After real-user validation, submit through Anthropic’s plugin submission form.
