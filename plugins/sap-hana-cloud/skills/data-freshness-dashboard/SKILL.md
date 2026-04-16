---
name: data-freshness-dashboard
description: Summarize data freshness and load activity across key HANA business tables. Produces a monitoring dashboard table showing latest record date, staleness in days, and recent load volumes. Optionally generates a live SQL VIEW in the work schema.
---

Sequence:
1. Ask for schema_name and optionally a list of key tables to monitor. If no list is provided, use `temporal-coverage-scan` results or run it now.
2. For each table in scope (up to 20), identify the best primary date column using this priority:
   - TRANSACTION_DATE > POSTING_DATE > EVENT_DATE > RECORD_DATE > CREATED_AT > CREATED_ON > any DATE column
   - Run `hana_describe_table` if column names are unknown.
3. For each table, run a freshness profile query (maxRows 1):
   ```sql
   SELECT
     '<table_name>'                                     AS TABLE_NAME,
     MAX(<primary_date_col>)                            AS LATEST_RECORD,
     DAYS_BETWEEN(MAX(<primary_date_col>), CURRENT_DATE) AS STALENESS_DAYS,
     COUNT(*)                                            AS TOTAL_ROWS,
     SUM(CASE WHEN <primary_date_col> >= ADD_DAYS(CURRENT_DATE, -1)   THEN 1 ELSE 0 END) AS ROWS_TODAY,
     SUM(CASE WHEN <primary_date_col> >= ADD_DAYS(CURRENT_DATE, -7)   THEN 1 ELSE 0 END) AS ROWS_LAST_7D,
     SUM(CASE WHEN <primary_date_col> >= ADD_DAYS(CURRENT_DATE, -30)  THEN 1 ELSE 0 END) AS ROWS_LAST_30D
   FROM "<schema>"."<table_name>"
   ```
4. Assign freshness status per table:
   - **GREEN**: STALENESS_DAYS ≤ 1
   - **AMBER**: STALENESS_DAYS 2–7
   - **ORANGE**: STALENESS_DAYS 8–30
   - **RED**: STALENESS_DAYS > 30
   - **EMPTY**: TOTAL_ROWS = 0
   - **NO_DATE**: no date column found — cannot assess freshness
5. Flag anomalies:
   - ROWS_TODAY = 0 for a table expected to have daily loads → LOAD_GAP today
   - ROWS_LAST_7D = 0 → NO_RECENT_LOADS (7-day gap)
   - TOTAL_ROWS > 0 but ROWS_LAST_30D = 0 → EFFECTIVELY_INACTIVE
   - TOTAL_ROWS significantly lower than expected (use `SYS.M_TABLE_STATISTICS` RECORD_COUNT if available) → POSSIBLE_TRUNCATION
6. Output dashboard table:
   `TABLE | LATEST_RECORD | STALENESS_DAYS | ROWS_TODAY | ROWS_LAST_7D | ROWS_LAST_30D | TOTAL_ROWS | STATUS | FLAGS`
7. Summarize: N GREEN, M AMBER, K RED, L EMPTY tables. List all flagged anomalies.
8. Optional — generate a monitoring SQL VIEW in work schema (reviewed write, goes through write guard):
   ```sql
   CREATE OR REPLACE VIEW "<work_schema>"."V_DATA_FRESHNESS_<SCHEMA>" AS
   SELECT '<table>' AS TABLE_NAME,
          MAX(<date_col>) AS LATEST_RECORD,
          DAYS_BETWEEN(MAX(<date_col>), CURRENT_DATE) AS STALENESS_DAYS,
          COUNT(*) AS TOTAL_ROWS,
          SUM(CASE WHEN <date_col> >= ADD_DAYS(CURRENT_DATE, -7) THEN 1 ELSE 0 END) AS ROWS_LAST_7D
   FROM "<schema>"."<table>"
   UNION ALL
   -- repeat for each monitored table
   ```
   Ask user before generating this view.

Guardrails:
- Use maxRows 1 for all profiling queries.
- If `SYS.M_TABLE_STATISTICS` is accessible, use RECORD_COUNT for TOTAL_ROWS where COUNT(*) would be too slow.
- The monitoring view DDL requires write_mode = ask or allow and goes through the write guard.
- Do not assume any table has a date column — always check `hana_describe_table` first.
- Tables with EMPTY status are not STALE — report them separately to avoid conflating empty tables with stale ones.
- This skill is read-only unless the user explicitly requests the monitoring view to be written.
