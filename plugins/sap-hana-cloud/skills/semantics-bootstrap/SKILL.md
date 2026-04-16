---
name: semantics-bootstrap
description: Help the user create or extend the optional HANA semantics JSON file used by `hana_explain_table`.
---

Sequence:
1. Run `hana_describe_table` and `hana_explain_table` for the target table.
2. Identify columns that need business descriptions or code maps.
3. Draft JSON entries in the same shape as the example semantics file.
4. Keep keys aligned with `SCHEMA.TABLE` or `DB.SCHEMA.TABLE` as appropriate.
Return a copy-paste JSON fragment, not only prose.
