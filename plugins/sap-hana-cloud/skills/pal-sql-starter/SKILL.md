---
name: pal-sql-starter
description: Generate a PAL-oriented SQL or SQLScript starting point using the currently available HANA metadata and source tables.
---

Sequence:
1. Start from a concrete feature or modeling goal.
2. Confirm the input table, key, and target columns.
3. If possible, inspect `SYS.AFL_AREAS` or `SYS.AFL_FUNCTIONS` for hints.
4. Draft a PAL-oriented SQL or SQLScript starter with placeholders the user can refine.
5. Explain what is verified versus what still needs SAP PAL reference checking.
Guardrails:
- Present PAL SQL as a starter template, not a guaranteed final script.
- Prefer explicit placeholders over invented exact object names.
