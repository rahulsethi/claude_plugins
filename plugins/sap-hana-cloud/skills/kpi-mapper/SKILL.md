---
name: kpi-mapper
description: Map business KPIs described in plain language to specific SQL expressions on discovered HANA tables. Validates column existence, handles edge cases (nulls, zero denominators), and produces a KPI catalog with SQL templates ready for use in dashboards or views.
---

Sequence:
1. Ask user to describe 3–7 KPIs in plain language. Examples:
   - "Monthly revenue"
   - "Customer churn rate"
   - "Average days to invoice payment"
   - "Headcount by department"
   - "Product return rate"
2. For each KPI, classify the KPI type:
   - **STOCK**: point-in-time count or value (headcount, active customers, current inventory)
   - **FLOW**: accumulated sum over a period (revenue, cost, volume)
   - **RATIO**: numerator divided by denominator, expressed as percentage (churn rate, return rate, margin)
   - **RATE**: events per unit time (orders per day, calls per agent per week)
   - **AVERAGE**: mean of a metric (avg days to pay, avg ticket value)
3. For each KPI, identify the source table and columns:
   a. Ask user if they know the source table — if yes, use it.
   b. If unknown, run `hana_list_tables` and `full-schema-profiler` (or use existing context) to find candidates.
   c. Run `hana_describe_table` on each candidate to confirm required columns exist.
4. Validate measure column exists and is numeric (DECIMAL, DOUBLE, INTEGER, BIGINT):
   ```sql
   SELECT COLUMN_NAME, DATA_TYPE_NAME
   FROM SYS.TABLE_COLUMNS
   WHERE SCHEMA_NAME = '<schema>' AND TABLE_NAME = '<table>'
     AND COLUMN_NAME = '<measure_col>'
   ```
5. Draft SQL expression per KPI type:
   - **STOCK**: `COUNT(DISTINCT <entity_key>) AS <kpi_name>`
   - **FLOW**: `SUM(<amount_col>) AS <kpi_name>`
   - **RATIO**: `ROUND(100.0 * SUM(<numerator_col>) / NULLIF(SUM(<denominator_col>), 0), 2) AS <kpi_name>`
   - **RATE**: `ROUND(1.0 * COUNT(CASE WHEN <event_flag> = 1 THEN 1 END) / NULLIF(DAYS_BETWEEN(MIN(<date>), MAX(<date>)), 0), 4) AS <kpi_name>`
   - **AVERAGE**: `ROUND(AVG(<metric_col>), 2) AS <kpi_name>`
6. Run a quick validation preview for each KPI (maxRows 5, GROUP BY time period):
   ```sql
   SELECT YEAR(<date_col>) AS YEAR, MONTH(<date_col>) AS MONTH,
          <kpi_sql_expression>
   FROM "<schema>"."<table>"
   WHERE <date_col> >= ADD_YEARS(CURRENT_DATE, -1)
   GROUP BY YEAR(<date_col>), MONTH(<date_col>)
   ORDER BY YEAR, MONTH
   ```
7. Output KPI catalog:
   `KPI_NAME | KPI_TYPE | SQL_EXPRESSION | SOURCE_TABLE | MEASURE_COLS | TIME_GRAIN | VALIDATION_STATUS | CAVEATS`
8. Flag:
   - MULTI_TABLE_KPI: KPI spans multiple tables — requires JOIN (hand off to `query-builder` or `star-schema-designer`)
   - AMBIGUOUS_SOURCE: multiple tables could plausibly serve this KPI
   - DENOMINATOR_RISK: ratio KPI with no NULLIF — auto-add NULLIF and flag
   - NEGATIVE_VALUES: if preview shows negative values for a measure expected to be positive
9. Generate a combined KPI summary SQL as a single SELECT (if all KPIs come from the same table or star schema).
10. Offer to generate a CREATE VIEW for the KPI summary in the work schema via `reviewed-write-executor`.

Guardrails:
- Never fabricate column names — always confirm against `hana_describe_table` before drafting SQL.
- Always use NULLIF in denominator expressions to prevent division-by-zero errors.
- Flag KPIs where source table is ambiguous — do not silently pick one.
- Keep validation previews small: maxRows 5, last 12 months only.
- This skill is read-only until the user explicitly requests a view or table to be written.
