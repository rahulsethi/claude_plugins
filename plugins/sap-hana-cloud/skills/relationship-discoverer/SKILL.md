---
name: relationship-discoverer
description: Discover formal FK constraints and implicit join relationships across all tables in a HANA schema. Foundation step for ontology and knowledge graph building.
---

Sequence:
1. Ask for schema_name (or use the configured default schema).
2. Query formal FK constraints via `hana_execute_query` with maxRows 200:
   ```sql
   SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME,
          REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
   FROM SYS.REFERENTIAL_CONSTRAINTS
   WHERE SCHEMA_NAME = '<schema>'
   ORDER BY TABLE_NAME, CONSTRAINT_NAME
   ```
   If `SYS.REFERENTIAL_CONSTRAINTS` is inaccessible, fall back to:
   ```sql
   SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME,
          REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
   FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
   WHERE CONSTRAINT_SCHEMA = '<schema>'
   ```
3. Query implicit relationships — columns shared across multiple tables — via `hana_execute_query` with maxRows 50:
   ```sql
   SELECT COLUMN_NAME,
          COUNT(DISTINCT TABLE_NAME) AS TABLE_COUNT,
          COUNT(DISTINCT DATA_TYPE_NAME) AS TYPE_VARIANTS,
          MIN(DATA_TYPE_NAME) AS SAMPLE_TYPE
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>'
   GROUP BY COLUMN_NAME
   HAVING COUNT(DISTINCT TABLE_NAME) > 1
   ORDER BY TABLE_COUNT DESC, COLUMN_NAME
   ```
4. For the top 20 shared column names by TABLE_COUNT, run a follow-up to list specific tables:
   ```sql
   SELECT TABLE_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>' AND COLUMN_NAME = '<col>'
   ORDER BY TABLE_NAME
   ```
5. Cross-reference: mark any shared column name that already has a confirmed FK as CONFIRMED. The remainder are INFERRED.
6. Exclude audit columns from relationship candidates (CREATED_AT, MODIFIED_AT, CHANGED_BY, CHANGED_AT, CREATED_BY, LAST_UPDATED — label these AUDIT, not relationship edges).
7. Flag type-inconsistent shared names (same name, different data types across tables) as LOW_CONFIDENCE — likely naming coincidence.
8. Output three sections:
   - **CONFIRMED edges**: `SOURCE_TABLE.COLUMN → TARGET_TABLE.COLUMN (constraint: CONSTRAINT_NAME)`
   - **INFERRED edges**: `COLUMN_NAME shared by N tables: [list] — CONFIDENCE: HIGH/LOW`
   - **Orphan tables**: tables with no FK relationships at all (potential islands)
9. Summarize: total confirmed edges, total inferred candidates, orphan count. Recommend `column-cross-mapper` for deeper implicit analysis and `entity-classifier` as the next step.

Guardrails:
- If SYS access fails entirely, note the privilege gap (`CATALOG READ` system privilege required) and continue with naming-pattern analysis only.
- Do not attempt to validate inferred relationships with sample data queries in this skill — that is join-hypothesis's job.
- Limit shared-name result to 50 rows to avoid overwhelming output.
- This skill is read-only. No writes are performed.
