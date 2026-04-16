---
name: pal-preflight
description: End-to-end readiness check before starting any PAL or hana_ml workflow.
---

This checks three things: database connectivity, PAL installation and roles, and modeling data readiness. It is broader than `pal-role-checker`, which only audits privilege grants.

Sequence:
1. Confirm connection with `hana_test_connection`.
2. Check whether PAL is installed on the instance:
   ```sql
   SELECT COUNT(*) AS PAL_AREA_COUNT FROM SYS.AFL_AREAS WHERE AREA_NAME = 'AFLPAL'
   ```
   - Count > 0: PAL is installed.
   - Count = 0 or view inaccessible: report BLOCKED for PAL SQL execution. Note that Python `hana_ml` lightweight algorithms (GradientBoostingTree via UnifiedClassification) may still work without full PAL stored-procedure access.
3. Check role grants for the current user:
   ```sql
   SELECT ROLE_NAME FROM PUBLIC.GRANTED_ROLES
   WHERE ROLE_NAME LIKE 'AFL%' OR ROLE_NAME LIKE '%PAL%' OR ROLE_NAME LIKE '%DATA SCIENTIST%'
   ```
   If the view is inaccessible or returns nothing, flag roles as UNCONFIRMED — a DBA check may be needed.
4. Confirm the work schema exists:
   ```sql
   SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME = '<work_schema>'
   ```
   If missing, report BLOCKED until the schema is created.
5. Confirm the planned source or feature table has the minimum data for the planned task:
   ```sql
   SELECT COUNT(*) AS ROW_COUNT FROM <source_table>
   ```
   Thresholds: at least 500 rows for binary classification, at least 1000 rows for regression or multiclass, at least 2 full seasonal cycles for time-series.
6. Return a preflight result: **READY**, **PARTIAL** (specify what is missing), or **BLOCKED** (specify why and what to fix).

Guardrails:
- Always distinguish "view not accessible" from "PAL not installed" — both look like query failures but require different fixes.
- Distinguish database readiness (PAL installed, roles granted) from modeling readiness (data quality, minimum rows).
