---
name: feature-table-materializer
description: Convert a reviewed feature plan into a materialized HANA feature table using reviewed SQL.
---

Sequence:
1. Confirm inputs: approved feature plan (grain, key column, score date, feature list) and target schema `${user_config.work_schema}`.
2. Draft the full feature SELECT with all aggregations anchored to the score date. Include the key column as the first column.
3. Verify grain before materializing. Run via `hana_execute_query`:
   ```sql
   SELECT COUNT(*) AS TOTAL_ROWS, COUNT(DISTINCT <key_col>) AS UNIQUE_KEYS
   FROM (<feature_select>)
   ```
   If TOTAL_ROWS differs from UNIQUE_KEYS, the grain is duplicated — diagnose the JOIN causing fan-out and fix the SQL before continuing.
4. Preview 5 sample rows:
   ```sql
   SELECT TOP 5 * FROM (<feature_select>)
   ```
   Check that feature columns contain plausible values and the key column is never NULL.
5. Choose materialization form:
   - `CREATE TABLE ... AS (SELECT ...)` — preferred when the feature set will be reused, passed to `hana_ml` by table reference, or is expensive to recompute
   - `CREATE VIEW ... AS SELECT ...` — acceptable for exploratory work when source tables update frequently and re-computing is fast
6. Name the object `<work_schema>.<entity>_FEATURES_<YYYYMMDD>` unless the user specifies a different name.
7. Run the CREATE statement through `reviewed-write-executor` — the PreToolUse hook will intercept it and ask for user confirmation before execution.
8. Postcheck after creation: run `SELECT COUNT(*) AS ROWS, COUNT(DISTINCT <key_col>) AS KEYS FROM <new_table>`. Confirm ROWS matches the grain-check count and no key column is NULL.

Guardrails:
- Never run the CREATE without a passing grain check and a clean sample preview.
- Always target `${user_config.work_schema}`, not a source or production schema.
- If the feature SELECT exceeds 10 seconds in preview, warn the user — the CREATE will take longer.
