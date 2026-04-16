---
name: landscape-recon
description: Run a quick HANA orientation flow. Use when the user asks what is available in the database or which schema to start with.
---

Work in this order:
1. Run `hana_test_connection`.
2. If it fails, stop and explain the failure.
3. Run `hana_list_schemas` with a sensible limit.
4. Shortlist likely business or curated schemas.
5. For one promising schema, run `hana_list_tables` and recommend the first table or two to inspect next.
Return: connection health, schema shortlist, recommended starting schema, and next best skill to use.
