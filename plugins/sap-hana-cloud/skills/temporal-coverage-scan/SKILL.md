---
name: temporal-coverage-scan
description: Analyze all date and timestamp columns across selected HANA tables to understand data freshness, historical depth, and time-series density. Critical before building time-series features, KPIs, or knowledge graph temporal annotations.
---

Sequence:
1. Ask for schema_name and optionally a table list. If no table list provided, auto-discover tables with date columns.
2. Run `hana_execute_query` to find all date/timestamp columns across the schema (maxRows 200):
   ```sql
   SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE_NAME, IS_NULLABLE
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>'
     AND DATA_TYPE_NAME IN ('DATE', 'TIMESTAMP', 'SECONDDATE', 'LONGDATE', 'DAYDATE')
   ORDER BY TABLE_NAME, COLUMN_NAME
   ```
3. For each table with date columns (limit 15 tables), select the best date column per table using this priority:
   - Priority 1: column name contains TRANSACTION_DATE, POSTING_DATE, EVENT_DATE, ORDER_DATE, RECORD_DATE
   - Priority 2: column name contains CREATED_AT, CREATED_ON, CREATION_DATE
   - Priority 3: column name contains MODIFIED_AT, UPDATED_AT, CHANGED_AT
   - Priority 4: first DATE/TIMESTAMP column by position
   Also select a secondary date column if available (e.g., VALID_TO, END_DATE) for range analysis.
4. For each selected table, run a temporal profile query (maxRows 1):
   ```sql
   SELECT
     MIN(<primary_date>) AS EARLIEST,
     MAX(<primary_date>) AS LATEST,
     DAYS_BETWEEN(MIN(<primary_date>), MAX(<primary_date>)) AS HISTORY_DAYS,
     DAYS_BETWEEN(MAX(<primary_date>), CURRENT_DATE) AS STALENESS_DAYS,
     SUM(CASE WHEN <primary_date> IS NULL THEN 1 ELSE 0 END) AS NULL_COUNT,
     COUNT(*) AS TOTAL_ROWS
   FROM "<schema>"."<table>"
   ```
5. Assign freshness tier per table:
   - **GREEN**: STALENESS_DAYS ≤ 1 (updated daily or more)
   - **AMBER**: 2–7 days stale
   - **ORANGE**: 8–30 days stale
   - **RED**: > 30 days stale
   - **UNKNOWN**: no date column or query failed
6. For tables with a secondary date column (VALID_TO, END_DATE), check active record counts:
   ```sql
   SELECT COUNT(*) AS CURRENTLY_ACTIVE
   FROM "<schema>"."<table>"
   WHERE <valid_to_col> >= CURRENT_DATE OR <valid_to_col> IS NULL
   ```
7. Check cross-table date alignment: do all FACT tables share the same LATEST date? Flag gaps > 7 days between FACT tables as TEMPORAL_MISALIGNMENT.
8. Output:
   `TABLE | PRIMARY_DATE_COL | EARLIEST | LATEST | HISTORY_DAYS | STALENESS_DAYS | NULL_PCT | FRESHNESS | ACTIVE_RECORDS`
9. Summarize: N GREEN, M AMBER, K RED tables. List temporal misalignments. Recommend stale tables for investigation.
10. Note SECONDDATE and LONGDATE types: these are HANA-native high-precision timestamps — functionally equivalent to TIMESTAMP for this analysis.

Guardrails:
- Limit to 2 date column profiles per table to avoid query bloat.
- Use maxRows 1 for all aggregate queries.
- If a table has zero rows, mark temporal coverage as EMPTY, not STALE.
- Do not scan Calculation Views for temporal data — they may require parameters.
- This skill is read-only.
