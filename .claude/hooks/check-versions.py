"""
PostToolUse hook: verify plugin.json and marketplace.json carry the same version.

Fires after any Edit or Write. Silently exits when neither versioned file was
the target; surfaces a clear error when versions diverge.
"""
import json
import sys

# Parse hook context from stdin (Claude Code passes tool call JSON here).
try:
    hook_input = json.load(sys.stdin)
    file_path = hook_input.get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)  # Can't parse — don't block.

# Only relevant when a versioned manifest was just edited.
relevant = ("plugin.json" in file_path) or ("marketplace.json" in file_path)
if not relevant:
    sys.exit(0)

try:
    with open("plugins/sap-datasphere/.claude-plugin/plugin.json", encoding="utf-8") as fh:
        plugin_ver = json.load(fh).get("version", "")
    with open(".claude-plugin/marketplace.json", encoding="utf-8") as fh:
        mkt_plugins = json.load(fh).get("plugins", [{}])
        market_ver = mkt_plugins[0].get("version", "") if mkt_plugins else ""
except FileNotFoundError:
    sys.exit(0)  # Manifest not found — skip silently.

if plugin_ver != market_ver:
    print(
        f"\n[VERSION MISMATCH]\n"
        f"  plugins/sap-datasphere/.claude-plugin/plugin.json  => {plugin_ver}\n"
        f"  .claude-plugin/marketplace.json (plugins[0])       => {market_ver}\n"
        f"\nUpdate both files to the same version before releasing."
    )
    sys.exit(1)

sys.exit(0)
