#!/usr/bin/env python3
import json
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get('tool_input') or {}
    path = str(tool_input.get('file_path') or '')
    normalized = path.replace('\\', '/')
    if 'plugins/sap-hana-cloud/' not in normalized:
        return 0

    message = (
        'You changed a sap-hana-cloud plugin file. Before declaring success, run '
        '`claude plugin validate ./plugins/sap-hana-cloud` and re-check the write guard '
        'if hooks or scripts changed.'
    )
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': message,
        }
    }))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
