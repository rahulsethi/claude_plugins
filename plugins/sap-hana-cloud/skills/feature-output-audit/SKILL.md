---
name: feature-output-audit
description: Audit a materialized feature table for modeling readiness before hana_ml consumption.
---

Sequence:
1. Confirm: table name, schema, expected grain (one row per what), key column, and target column if labeled.
2. Check row count and key uniqueness via `hana_execute_query`:
   ```sql
   SELECT COUNT(*) AS TOTAL_ROWS, COUNT(DISTINCT <key_col>) AS UNIQUE_KEYS FROM <schema>.<table>
   ```
   If TOTAL_ROWS > UNIQUE_KEYS, the grain is duplicated — report the difference and stop. The table must be rebuilt before use.
3. For each feature column, check null rate (run one column at a time for large tables):
   ```sql
   SELECT
     SUM(CASE WHEN <col> IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS NULL_PCT
   FROM <schema>.<table>
   ```
   - NULL_PCT > 50: flag as HIGH NULL
   - NULL_PCT = 100: flag as EMPTY
4. Check for constant features:
   ```sql
   SELECT COUNT(DISTINCT <col>) AS DISTINCT_VALS FROM <schema>.<table>
   ```
   Any column with DISTINCT_VALS = 1 is CONSTANT — it adds no information and should be dropped.
5. Check the date range of the score date or event date column:
   ```sql
   SELECT MIN(<date_col>) AS EARLIEST, MAX(<date_col>) AS LATEST FROM <schema>.<table>
   ```
   Warn if: the range is shorter than 30 days for monthly-scored entities, or if LATEST is in the future relative to today.
6. Sample 5 rows via `hana_execute_query SELECT TOP 5 * FROM <table>`. Scan visually for implausible values (negative counts, extreme outliers, date columns containing Unix epoch values).
7. Return an audit summary:
   - Total row count and key uniqueness status (PASS / FAIL with duplicate count)
   - List of HIGH NULL features with their null percentages
   - List of EMPTY features
   - List of CONSTANT features
   - Date range and any warnings
   - Overall verdict: **READY**, **REVIEW NEEDED** (list issues to fix), or **BLOCKED** (grain or key failure — rebuild required)

Guardrails:
- Run all checks as SELECT only — never modify the table.
- Label any check that used `TOP 5` or sampling as "based on preview, not full scan".
- A BLOCKED verdict means the table must be rebuilt before `hana_ml` consumption.
