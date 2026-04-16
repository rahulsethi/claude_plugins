---
name: procedure-catalog
description: Discover and document stored procedures and scalar/table functions in a HANA schema. Identifies PAL algorithm procedures automatically. Uses SYS.PROCEDURES, SYS.FUNCTIONS, and SYS.PROCEDURE_PARAMETERS.
---

Sequence:
1. Ask for schema_name. Also ask if the user wants to include PAL system procedures from `_SYS_AFL` schema (default: show summary count only).
2. Run `hana_execute_query` to list procedures in the schema (maxRows 100):
   ```sql
   SELECT PROCEDURE_NAME,
          PROCEDURE_TYPE,
          IS_VALID,
          INPUT_PARAMETER_COUNT,
          OUTPUT_PARAMETER_COUNT,
          OWNER_NAME,
          CREATE_TIME,
          COMMENTS
   FROM SYS.PROCEDURES
   WHERE SCHEMA_NAME = '<schema>'
   ORDER BY PROCEDURE_TYPE, PROCEDURE_NAME
   ```
3. Run `hana_execute_query` to list scalar and table functions (maxRows 100):
   ```sql
   SELECT FUNCTION_NAME,
          FUNCTION_TYPE,
          IS_VALID,
          INPUT_PARAMETER_COUNT,
          OWNER_NAME,
          CREATE_TIME,
          COMMENTS
   FROM SYS.FUNCTIONS
   WHERE SCHEMA_NAME = '<schema>'
   ORDER BY FUNCTION_TYPE, FUNCTION_NAME
   ```
4. If user wants PAL procedures, separately query `_SYS_AFL` for algorithm names:
   ```sql
   SELECT PROCEDURE_NAME, PROCEDURE_TYPE, INPUT_PARAMETER_COUNT, OUTPUT_PARAMETER_COUNT
   FROM SYS.PROCEDURES
   WHERE SCHEMA_NAME = '_SYS_AFL'
   ORDER BY PROCEDURE_NAME
   ```
   Present as a summary count grouped by algorithm family (PAL_KMEANS, PAL_LINEAR_REGRESSION, etc.) — do not expand all.
5. For each user-schema procedure (up to 15), fetch parameter signature:
   ```sql
   SELECT PARAMETER_NAME, DATA_TYPE_NAME, TABLE_TYPE_NAME,
          PARAMETER_TYPE, HAS_DEFAULT_VALUE, POSITION
   FROM SYS.PROCEDURE_PARAMETERS
   WHERE SCHEMA_NAME = '<schema>' AND PROCEDURE_NAME = '<proc>'
   ORDER BY POSITION
   ```
6. Identify procedure categories:
   - PAL_* prefix or SCHEMA = _SYS_AFL → PAL ALGORITHM (requires AFL_EXECUTE privilege to CALL)
   - Name contains ETL, LOAD, REFRESH, SYNC → DATA PIPELINE
   - Name contains CLEAN, VALIDATE, CHECK → DATA QUALITY
   - Name contains REPORT, EXPORT, EXTRACT → REPORTING
   - Otherwise → BUSINESS LOGIC
7. Flag invalid procedures (`IS_VALID = FALSE`) — these have compilation errors or missing object dependencies.
8. Output:
   `OBJECT_NAME | OBJECT_TYPE | CATEGORY | IN_PARAMS | OUT_PARAMS | IS_VALID | SIGNATURE_SUMMARY`
9. Summarize: N procedures, M functions, K PAL algorithms (system), L invalid objects.
10. Recommend `pal-preflight` if PAL procedures are found and the user wants to execute them.

Guardrails:
- Do not CALL any procedure. This skill is catalog discovery only.
- Invalid procedures should be flagged, not ignored — they may indicate broken dependencies worth investigating.
- If `SYS.PROCEDURES` is inaccessible, advise `CATALOG READ` system privilege.
- PAL procedures in `_SYS_AFL` cannot be directly inspected without AFL_EXECUTE and AFL_PACKAGEADMIN roles — note this clearly.
- This skill is read-only.
