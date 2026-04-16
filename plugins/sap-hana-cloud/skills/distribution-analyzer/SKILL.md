---
name: distribution-analyzer
description: Value distribution analysis for categorical and code columns in a HANA table. Shows top values, rare values, null rates, and suspicious null-encoded strings. Useful for ontology value enumeration, data quality pre-work, and feature engineering preparation.
---

Sequence:
1. Ask for schema_name and table_name. Optionally accept a specific column list — if not provided, auto-detect categorical columns.
2. Run `hana_describe_table` to get the full column list with types and lengths.
3. Auto-detect categorical columns if no list provided. Target columns that are:
   - VARCHAR/NVARCHAR with length ≤ 50, OR
   - Column name contains: STATUS, TYPE, CODE, FLAG, CATEGORY, SEGMENT, REGION, CHANNEL, GRADE, TIER, PRIORITY, CLASS, GROUP, KIND, MODE
   Exclude columns likely to be free text: DESCRIPTION, COMMENTS, NOTES, REMARKS, TEXT, REASON (length > 200).
4. Confirm list of target columns with user (max 8 columns per run). Skip columns the user excludes.
5. For each target column, run a value distribution query (maxRows 20):
   ```sql
   SELECT
     <col> AS VALUE,
     COUNT(*) AS FREQUENCY,
     ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS PCT_OF_TOTAL
   FROM "<schema>"."<table>"
   WHERE <col> IS NOT NULL
   GROUP BY <col>
   ORDER BY FREQUENCY DESC
   LIMIT 15
   ```
6. Run true cardinality check (maxRows 1):
   ```sql
   SELECT COUNT(DISTINCT <col>) AS CARDINALITY,
          SUM(CASE WHEN <col> IS NULL THEN 1 ELSE 0 END) AS NULL_COUNT,
          COUNT(*) AS TOTAL_ROWS
   FROM "<schema>"."<table>"
   ```
7. Run suspicious null-encoding check (maxRows 1):
   ```sql
   SELECT SUM(CASE WHEN <col> IN ('N/A', 'NA', 'NULL', 'UNKNOWN', 'NONE',
                                   'MISSING', '-', '?', '', ' ', '0', 'NOT APPLICABLE')
               THEN 1 ELSE 0 END) AS SUSPICIOUS_NULL_COUNT
   FROM "<schema>"."<table>"
   ```
8. For each column, output:
   - Distribution table: top 15 values with frequency and percentage
   - Null rate: `NULL_COUNT / TOTAL_ROWS * 100`
   - Suspicious null count and percentage
   - Cardinality assessment: LOW (< 10), MEDIUM (10–100), HIGH (> 100)
9. Flag:
   - DOMINANT_VALUE: top value accounts for > 80% of non-null rows (may be a default or placeholder)
   - HIGH_CARDINALITY: cardinality > 200 (not truly categorical — may be a text/code field, not a code table)
   - SUSPICIOUS_NULLS: suspicious null count > 1% of total rows
   - HIGH_NULL_RATE: null rate > 20%
10. If CARDINALITY < 30 and suspicious nulls are low, output an `owl:oneOf` candidate list for ontology use.
11. Recommend `semantics-bootstrap` to document code-to-label mappings for flagged columns.

Guardrails:
- Do not run distribution analysis on columns with CARDINALITY > 500 — warn and skip.
- Exclude free-text columns (length > 200) from auto-detection.
- Use maxRows 20 for distribution queries, maxRows 1 for aggregate checks.
- If a column's distribution query takes too long (very large table), note this and suggest adding a WHERE clause filter.
- This skill is read-only.
