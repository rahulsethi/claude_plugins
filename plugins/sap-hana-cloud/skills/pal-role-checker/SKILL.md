---
name: pal-role-checker
description: Audit PAL-related database roles and privileges for the current technical user.
---

Use this when `pal-preflight` returned PARTIAL or BLOCKED on roles, or when you need to produce a specific grant list for a DBA.

Sequence:
1. Confirm connection with `hana_test_connection`.
2. List AFL function areas — this also tests whether the current user can read `SYS.AFL_FUNCTIONS`:
   ```sql
   SELECT AREA_NAME, COUNT(*) AS FUNCTION_COUNT
   FROM SYS.AFL_FUNCTIONS
   GROUP BY AREA_NAME
   ORDER BY AREA_NAME
   ```
   If this is blocked, note that `SYS.AFL_FUNCTIONS` requires the `AFL__SYS_AFL_AFLPAL_EXECUTE` privilege.
3. Check granted roles via the public view:
   ```sql
   SELECT ROLE_NAME FROM PUBLIC.GRANTED_ROLES
   WHERE ROLE_NAME LIKE 'AFL%'
      OR ROLE_NAME LIKE '%PAL%'
      OR ROLE_NAME LIKE '%DATA SCIENTIST%'
   ```
4. If the above is inaccessible, try the system view:
   ```sql
   SELECT ROLE_NAME FROM SYS.EFFECTIVE_ROLES
   WHERE ROLE_NAME LIKE 'AFL%'
   ```
5. Check for direct EXECUTE privileges on PAL procedures if role queries return empty:
   ```sql
   SELECT PRIVILEGE, OBJECT_NAME FROM SYS.EFFECTIVE_PRIVILEGES
   WHERE OBJECT_NAME LIKE 'PAL%' OR OBJECT_NAME LIKE 'AFL%'
   ```
6. Summarize each query result individually: confirmed, empty, or blocked. State the exact privilege or role grant that is missing if identifiable.
7. Recommend the next step: proceed with PAL SQL, use Python `hana_ml` lightweight mode, or escalate to a DBA with the specific `GRANT` statement needed.

Guardrails:
- Report each check result separately — do not collapse all failures into one message.
- Distinguish missing privileges (PAL installed but not granted) from missing objects (PAL not installed at all).
