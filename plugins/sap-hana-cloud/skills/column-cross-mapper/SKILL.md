---
name: column-cross-mapper
description: Find all HANA tables in a schema that share a common column name. Ranks by occurrence count to reveal hub entities, shared domains, and implicit join paths — especially useful when FK constraints are absent.
---

Sequence:
1. Ask for schema_name. Ask if a table prefix or column name pattern filter is needed.
2. Run `hana_execute_query` with maxRows 100 to get all shared column names:
   ```sql
   SELECT COLUMN_NAME,
          COUNT(DISTINCT TABLE_NAME) AS TABLE_COUNT,
          COUNT(DISTINCT DATA_TYPE_NAME) AS TYPE_VARIANTS,
          MIN(DATA_TYPE_NAME) AS SAMPLE_TYPE,
          MAX(LENGTH) AS MAX_LENGTH
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>'
   GROUP BY COLUMN_NAME
   HAVING COUNT(DISTINCT TABLE_NAME) > 1
   ORDER BY TABLE_COUNT DESC, COLUMN_NAME
   ```
3. For the top 25 column names by TABLE_COUNT, run a detail query to list the specific tables (maxRows 50 per column):
   ```sql
   SELECT TABLE_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE, POSITION
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>' AND COLUMN_NAME = '<col>'
   ORDER BY TABLE_NAME
   ```
4. Classify each shared column name into one of these roles:
   - **HUB_KEY**: ends in _ID, _KEY, or _NR; same type across all tables; high TABLE_COUNT → likely shared entity identifier, candidate graph hub
   - **SHARED_DOMAIN**: name contains STATUS, TYPE, CODE, FLAG, CATEGORY → shared value domain / reference lookup
   - **AUDIT**: name is CREATED_AT, CREATED_BY, MODIFIED_AT, CHANGED_BY, LAST_UPDATED, MANDT → audit column, not a relationship
   - **DATE_MARKER**: pure date/timestamp column (VALID_FROM, VALID_TO, POSTING_DATE) shared across tables → temporal alignment candidate
   - **AMBIGUOUS**: type-inconsistent across tables → likely naming coincidence, LOW_CONFIDENCE
5. For HUB_KEY candidates, estimate join selectivity with a small preview (top 2 candidates only):
   ```sql
   SELECT COUNT(DISTINCT <col>) AS UNIQUE_VALS, COUNT(*) AS TOTAL_ROWS
   FROM "<schema>"."<table>" WHERE <col> IS NOT NULL
   ```
6. Output ranked table:
   `RANK | COLUMN_NAME | TABLE_COUNT | TABLES | TYPE_CONSISTENT | ROLE | CONFIDENCE | JOIN_CANDIDATE`
7. Summarize: N hub keys found, M shared domains, K audit columns excluded, L ambiguous.
8. Recommend top 5 HUB_KEY columns for `join-hypothesis` validation.
9. Feed the HUB_KEY list directly into `relationship-discoverer` and `knowledge-graph-builder` as INFERRED edges.

Guardrails:
- If `SYS.TABLE_COLUMNS` is inaccessible, report the privilege gap (`CATALOG READ` required) and offer to run `hana_describe_table` on individual tables manually.
- Exclude audit columns from all join and relationship recommendations — label them AUDIT and suppress from ranked output.
- Type-inconsistent shared names are LOW_CONFIDENCE by default — do not recommend them as join paths without user confirmation.
- Cap detail queries at 25 column names to avoid session length limits.
- This skill is read-only.
