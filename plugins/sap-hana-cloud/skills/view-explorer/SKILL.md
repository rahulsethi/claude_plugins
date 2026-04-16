---
name: view-explorer
description: Discover and inspect views in a HANA schema using system catalog queries. Covers SQL views, Calculation Views, and join views. No dedicated MCP tool exists for views — this skill uses hana_execute_query against SYS.VIEWS and SYS.VIEW_COLUMNS.
---

Sequence:
1. Ask for schema_name.
2. Run `hana_execute_query` to list all views in the schema (maxRows 100):
   ```sql
   SELECT VIEW_NAME,
          VIEW_TYPE,
          IS_COLUMN_VIEW,
          HAS_PARAMETERS,
          LENGTH(VIEW_DEFINITION) AS DEFINITION_LENGTH,
          COMMENTS,
          CREATE_TIME
   FROM SYS.VIEWS
   WHERE SCHEMA_NAME = '<schema>'
   ORDER BY VIEW_TYPE, VIEW_NAME
   ```
3. Group views by type:
   - `IS_COLUMN_VIEW = TRUE` → CALCULATION VIEW (SAP HANA analytic model, not editable via SQL)
   - `VIEW_TYPE = 'ROW'` → Standard SQL View
   - `VIEW_TYPE = 'JOIN'` → Join View (deprecated in newer HANA versions)
   - `VIEW_TYPE = 'COLUMN'` AND `IS_COLUMN_VIEW = FALSE` → Column Store View
4. For each SQL view (up to 10, prioritizing ROW type), fetch column details:
   ```sql
   SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE,
          POSITION, COMMENTS
   FROM SYS.VIEW_COLUMNS
   WHERE SCHEMA_NAME = '<schema>' AND VIEW_NAME = '<view>'
   ORDER BY POSITION
   ```
5. For Calculation Views, note: "Calculation Views are HANA-native analytical models managed via SAP BAS or HANA Studio. Column metadata is available but view definition XML is not accessible via this MCP tool surface."
6. For SQL views (up to 5), fetch the definition text to identify source tables:
   ```sql
   SELECT VIEW_DEFINITION
   FROM SYS.VIEWS
   WHERE SCHEMA_NAME = '<schema>' AND VIEW_NAME = '<view>'
   ```
   Parse source table references from the definition and list them as UPSTREAM_TABLES.
7. Output summary:
   `VIEW_NAME | VIEW_TYPE | COLUMN_COUNT | UPSTREAM_TABLES | HAS_PARAMS | PURPOSE_NOTES`
8. Flag views with `HAS_PARAMETERS = TRUE` — these are parameterized views that require input values to query.
9. Recommend `lineage-graph` for views where full upstream dependency tracing is needed.
10. If any views are found that match the user's table of interest from other skills, highlight them.

Guardrails:
- If `SYS.VIEWS` is inaccessible, report the privilege gap (`CATALOG READ` system privilege is required) and halt gracefully.
- Limit column detail queries to 10 views. List remaining view names only.
- Do not attempt to SELECT from Calculation Views directly — they may require specific parameters or roles.
- VIEW_DEFINITION parsing is best-effort text extraction, not full SQL parsing. Surface table names as hints, not guaranteed dependencies.
- This skill is read-only.
