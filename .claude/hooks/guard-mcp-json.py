"""
PreToolUse hook: warn before editing the plugin's shipped .mcp.json.

The correct format for a Claude Code plugin .mcp.json is a flat object keyed
by server name — NO 'mcpServers' wrapper. This hook fires a reminder before
any edit to prevent accidental regression.
"""
import json
import sys

try:
    hook_input = json.load(sys.stdin)
    file_path = hook_input.get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)

if "plugins/sap-datasphere/.mcp.json" not in file_path:
    sys.exit(0)

print(
    "\n[GUARD] Editing the plugin's shipped .mcp.json.\n"
    "\n"
    "  CORRECT format (flat, server name as top-level key):\n"
    '  { "sap-datasphere": { "command": "...", "env": { ... } } }\n'
    "\n"
    "  WRONG format (do NOT use the mcpServers wrapper):\n"
    '  { "mcpServers": { "sap-datasphere": { ... } } }\n'
)
# Warning only — do not block the edit (exit 0).
sys.exit(0)
