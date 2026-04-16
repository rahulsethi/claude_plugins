#!/usr/bin/env python3
import argparse
import json
import re
import sys

ALWAYS_BLOCK = {
    'DROP',
    'TRUNCATE',
    'SHUTDOWN',
}

# Two-word prefixes that are hard-blocked regardless of write_mode.
# 'ALTER' alone is in MUTATING_KEYWORDS (ALTER TABLE is a legitimate reviewed write),
# but 'ALTER SYSTEM' modifies HANA system config and must never be allowed.
ALWAYS_BLOCK_PREFIXES = {
    'ALTER SYSTEM',
}

MUTATING_KEYWORDS = {
    'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'UPSERT', 'CREATE', 'ALTER', 'CALL', 'DO', 'REPLACE'
}


def strip_leading_comments(sql: str) -> str:
    text = (sql or '').lstrip()
    changed = True
    while changed:
        changed = False
        if text.startswith('--'):
            newline = text.find('\n')
            text = '' if newline == -1 else text[newline + 1 :].lstrip()
            changed = True
        elif text.startswith('/*'):
            end = text.find('*/')
            text = '' if end == -1 else text[end + 2 :].lstrip()
            changed = True
    return text


def normalize(sql: str) -> str:
    text = strip_leading_comments(sql).strip()
    text = re.sub(r';+\s*$', '', text).strip()
    return text


def first_keyword(sql: str) -> str:
    text = normalize(sql)
    if not text:
        return ''
    match = re.match(r'([A-Z_]+)', text.upper())
    return match.group(1) if match else ''


def is_single_selectable(sql: str) -> bool:
    text = normalize(sql)
    if not text:
        return False
    if ';' in text:
        return False
    upper = text.upper()
    return upper.startswith('SELECT') or upper.startswith('WITH')


def emit(decision: str, reason: str, additional_context: str = '') -> None:
    payload = {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': decision,
            'permissionDecisionReason': reason,
        }
    }
    if additional_context:
        payload['hookSpecificOutput']['additionalContext'] = additional_context
    print(json.dumps(payload))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-mode', default='ask')
    parser.add_argument('--work-schema', default='')
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get('tool_input') or {}
    query = tool_input.get('query')
    if not isinstance(query, str) or not query.strip():
        return 0

    write_mode = (args.write_mode or 'ask').strip().lower() or 'ask'
    work_schema = (args.work_schema or '').strip()
    sql = normalize(query)
    if not sql:
        return 0

    upper = sql.upper()

    if is_single_selectable(sql):
        return 0

    if ';' in upper:
        emit(
            'deny',
            'Blocked multi-statement SQL. Submit one reviewed statement at a time through hana_execute_query.'
        )
        return 0

    keyword = first_keyword(sql)
    delete_without_where = keyword == 'DELETE' and ' WHERE ' not in f' {upper} '
    prefix_blocked = any(upper.startswith(p) for p in ALWAYS_BLOCK_PREFIXES)
    if keyword in ALWAYS_BLOCK or delete_without_where or prefix_blocked:
        emit(
            'deny',
            'Blocked potentially destructive SQL. Use a safer reviewed workflow and avoid destructive statements in Claude Code.'
        )
        return 0

    if keyword in MUTATING_KEYWORDS or keyword:
        base_reason = (
            f'Non-read-only SQL detected ({keyword or "UNKNOWN"}). Review target objects, row counts, '
            'and rollback path before execution.'
        )
        if work_schema:
            base_context = (
                f'Preferred work schema for reviewed writes: {work_schema}. Use it for feature tables, '
                'PAL outputs, and staging tables unless you intentionally need another target.'
            )
        else:
            base_context = 'No work schema is configured. Prefer a dedicated non-source schema for reviewed writes.'

        if write_mode == 'deny':
            emit('deny', f'Write mode is deny. {base_reason}')
            return 0
        if write_mode == 'allow':
            emit('allow', f'Write mode is allow. {base_reason}', base_context)
            return 0
        emit('ask', f'Write mode is ask. {base_reason}', base_context)
        return 0

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
