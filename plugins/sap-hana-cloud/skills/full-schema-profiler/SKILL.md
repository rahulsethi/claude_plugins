---
name: full-schema-profiler
description: Multi-table data catalog profiler. For each table in a schema, collects row counts, key column null rates, date ranges, and status column cardinality in one pass. Produces a catalog card per table. Extends quality-scan to the whole schema.
---

Sequence:
1. Ask for schema_name and optionally a table name prefix filter. Ask for max tables to profile (default 15, max 25).
2. Run `hana_list_tables` to get the full table list. If filtered by prefix, apply it.
3. For each table in the list (up to 15 at a time):
   a. Attempt fast row count via SYS statistics (preferred — avoids full scan):
      ```sql
      SELECT RECORD_COUNT
      FROM SYS.M_TABLE_STATISTICS
      WHERE SCHEMA_NAME = '<schema>' AND TABLE_NAME = '<table>'
      ```
      If this returns NULL or is inaccessible, fall back to:
      ```sql
      SELECT COUNT(*) AS ROW_COUNT FROM "<schema>"."<table>"
      ```
   b. Run `hana_describe_table` to get column list, types, and nullability.
   c. Identify profiling targets per table:
      - Date columns (DATE, TIMESTAMP, SECONDDATE): pick up to 2 (prefer TRANSACTION_DATE > POSTING_DATE > CREATED_AT > any DATE)
      - Key columns (INTEGER/BIGINT named *_ID, *_KEY, *_NR): pick 1
      - Status/type columns (VARCHAR with name *STATUS, *TYPE, *CODE, *FLAG): pick up to 2
   d. Build a combined profiling query per table (maxRows 1):
      ```sql
      SELECT
        COUNT(*) AS ROW_COUNT,
        MIN(<date_col1>) AS DATE1_MIN, MAX(<date_col1>) AS DATE1_MAX,
        SUM(CASE WHEN <date_col1> IS NULL THEN 1 ELSE 0 END) AS DATE1_NULLS,
        SUM(CASE WHEN <key_col> IS NULL THEN 1 ELSE 0 END) AS KEY_NULLS,
        COUNT(DISTINCT <status_col>) AS STATUS_CARDINALITY
      FROM "<schema>"."<table>"
      ```
4. Assemble a catalog card per table:
   ```
   TABLE: <name>
   Rows:         <count>
   Date range:   <min> → <max> (<N> days)
   Key nulls:    <count> (<pct>%)
   Status vals:  <cardinality> distinct
   Flags:        EMPTY / STALE / NO_DATE / HIGH_KEY_NULLS
   ```
5. Assign flags:
   - EMPTY: row count = 0
   - STALE: max date > 180 days before CURRENT_DATE
   - NO_DATE: no date column found
   - HIGH_KEY_NULLS: key column null rate > 5%
   - LARGE: row count > 10M (may need extra care in join queries)
6. Output the full catalog table:
   `TABLE | ROW_COUNT | DATE_MIN | DATE_MAX | HISTORY_DAYS | KEY_NULL_PCT | STATUS_CARDINALITY | FLAGS`
7. Summarize: N tables profiled, M flags raised, top 3 largest tables, tables needing attention (flagged).
8. Offer to export catalog as a JSON structure suitable for use with `semantics-bootstrap`.

Guardrails:
- If a table profiling query fails or times out, mark as PROFILE_FAILED and continue — do not halt the whole run.
- Use `SYS.M_TABLE_STATISTICS` for row counts whenever possible to avoid slow COUNT(*) on large tables.
- Cap at 25 tables per run. For schemas with more tables, ask user to filter by prefix or provide a priority list.
- Use maxRows 1 for all aggregate profiling queries.
- This skill is read-only.
