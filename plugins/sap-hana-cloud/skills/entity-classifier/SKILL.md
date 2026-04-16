---
name: entity-classifier
description: Classify all tables in a HANA schema by their likely ontological role — FACT, DIMENSION, MASTER, REFERENCE, STAGING, or ANALYTICAL. Required before knowledge-graph-builder.
---

Sequence:
1. Ask for schema_name. Ask if a table name prefix filter is needed (e.g., only tables starting with "SALES_").
2. Run `hana_list_tables` to retrieve the full table list. If > 30 tables, ask user to confirm or filter.
3. For each table (batch in groups of 10 to avoid timeouts):
   a. Run `hana_describe_table` to get column count, column names, and data types.
   b. Run `hana_execute_query` for row count (maxRows 1):
      ```sql
      SELECT COUNT(*) AS ROW_COUNT FROM "<schema>"."<table>"
      ```
      If this times out or fails, mark ROW_COUNT = UNKNOWN.
4. Classify each table using these ordered rules (first match wins):
   - **STAGING**: table name starts with STAG_, STG_, TMP_, TEMP_, or ends with _LOAD, _STAGE, _LANDING → STAGING
   - **REFERENCE**: ROW_COUNT < 500 AND column count ≤ 5 AND all columns VARCHAR/NVARCHAR → REFERENCE (lookup/code table)
   - **DIMENSION**: ROW_COUNT < 50,000 AND mostly VARCHAR columns AND presence of a CODE or DESCRIPTION or NAME column → DIMENSION
   - **MASTER**: ROW_COUNT < 500,000 AND has a clean integer or UUID primary-key-like column AND no dominant date/timestamp column pattern → MASTER
   - **FACT**: ROW_COUNT > 100,000 AND has 2+ date/timestamp columns AND has DECIMAL/DOUBLE measure columns → FACT
   - **ANALYTICAL**: table name contains CALC_, CUBE_, AGG_, SNAPSHOT_, or ends in _HIST, _SUMMARY, _REPORT → ANALYTICAL
   - **UNKNOWN**: insufficient signal to classify
5. For tables with ambiguous classification, note the competing signals in RATIONALE.
6. Return a classification table:
   `TABLE_NAME | ENTITY_TYPE | ROW_COUNT | COLUMN_COUNT | KEY_SIGNALS | CLASSIFICATION_RATIONALE`
7. Summarize counts: N FACT, M DIMENSION, K MASTER, L REFERENCE, P STAGING, Q ANALYTICAL, R UNKNOWN.
8. Flag: tables with ROW_COUNT = 0 (empty), tables with no date columns (may be reference/master), tables that share the same prefix (likely a family).

Guardrails:
- Classification is heuristic only — always present RATIONALE so the user can override.
- Cap at 30 tables per run. If schema exceeds this, process the most business-relevant tables first (ask user).
- Row count queries on very large tables (>100M rows) may be slow — note this and use `APPROX_COUNT_DISTINCT` or `RECORD_COUNT` from SYS.M_TABLE_STATISTICS as a fallback:
  ```sql
  SELECT TABLE_NAME, RECORD_COUNT FROM SYS.M_TABLE_STATISTICS
  WHERE SCHEMA_NAME = '<schema>' AND TABLE_NAME = '<table>'
  ```
- Do not confuse SQL VIEWs with TABLEs — if `hana_list_tables` returns views, note them separately and recommend `view-explorer`.
- This skill is read-only.
