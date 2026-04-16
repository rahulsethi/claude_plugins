---
name: write-safety-primer
description: Explain exactly how reviewed writes work in this plugin.
---

Explain these points clearly:
1. `hana_execute_query` can run non-read-only SQL.
2. The plugin ships a `PreToolUse` hook that inspects SQL first.
3. Write mode is `${user_config.write_mode}`.
4. The recommended target for feature tables is `${user_config.work_schema}`.
5. Safe workflow: plan the write, preview the source `SELECT`, confirm target schema, then execute the reviewed DDL or DML.
6. Destructive statements remain a bad idea in Claude Code.
Keep this skill educational and practical.
