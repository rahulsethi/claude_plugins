---
name: release-smoke-test
description: Run the full manual smoke-test sequence for the sap-hana-cloud plugin before any release.
---

Run all stages in order. Do not mark release-ready until every hook test in Stage 5 passes.

---

## Stage 1 — Validation (terminal, repo root)

```bash
claude plugin validate .
claude plugin validate ./plugins/sap-hana-cloud
```
Pass: both print `✔ Validation passed`, exit 0.

---

## Stage 2 — Local plugin-dir load

```bash
claude --plugin-dir ./plugins/sap-hana-cloud
```
Inside the session:
```
/help
/agents
```
Pass: `sap-hana-cloud` visible in `/help`. All 10 agents listed in `/agents`:
`hana-analyst`, `hana-researcher`, `hana-curated-dataset-scout`, `hana-quality-reviewer`,
`hana-sql-engineer`, `hana-write-operator`, `hana-feature-engineer`, `hana-ml-engineer`,
`hana-pal-operator`, `hana-platform-advisor`

Exit this session before Stage 3.

---

## Stage 3 — Marketplace add and install

```
/plugin marketplace add ./
/plugin install sap-hana-cloud@sethir-marketplace
/reload-plugins
/help
```
Pass: no errors; `sap-hana-cloud` visible with skills prefixed `sap-hana-cloud:`.

---

## Stage 4 — Read-only discovery

```
/sap-hana-cloud:connection-doctor
```
Pass (live): connection confirmed. Pass (no tenant): clear message about which config field is missing — not a hang.

```
/sap-hana-cloud:landscape-recon
```
Pass: schema list returned; system schemas de-emphasised.

```
/sap-hana-cloud:table-explorer
```
Pass: Claude asks which schema to explore; no write attempted.

```
/sap-hana-cloud:plugin-doctor
```
Pass: hook active confirmed; work schema status shown; MCP tool list present.

---

## Stage 5 — Write hook behavior (highest priority)

Run each sub-test exactly as written. Each expects a specific hook outcome.

**5a — SELECT must pass with no hook prompt**
Prompt Claude: `Using hana_execute_query, run: SELECT TOP 5 * FROM SYS.TABLES`
Pass: query runs immediately, no confirmation dialog.

**5b — CREATE TABLE must trigger a confirmation prompt**
Prompt Claude:
```
Using hana_execute_query, run:
CREATE TABLE ML_WORK.SMOKE_TEST_TABLE (ID INTEGER, LABEL NVARCHAR(10))
```
Pass: hook intercepts; Claude presents the SQL and waits for user approval. Deny it.

**5c — DROP TABLE must be hard-blocked without a prompt**
Prompt Claude: `Using hana_execute_query, run: DROP TABLE ML_WORK.SMOKE_TEST_TABLE`
Pass: hook denies immediately; no confirmation dialog; message references destructive SQL.

**5d — DELETE without WHERE must be hard-blocked**
Prompt Claude: `Using hana_execute_query, run: DELETE FROM ML_WORK.SMOKE_TEST_TABLE`
Pass: hook denies immediately; message references missing WHERE clause.

**5e — Multi-statement must be hard-blocked**
Prompt Claude: `Using hana_execute_query, run: INSERT INTO ML_WORK.T1 VALUES (1); INSERT INTO ML_WORK.T2 VALUES (2)`
Pass: hook denies immediately; message references multi-statement SQL.

---

## Stage 6 — PAL and hana_ml generation

```
/sap-hana-cloud:pal-preflight
```
Pass: returns READY, PARTIAL, or BLOCKED with a specific reason.

```
/sap-hana-cloud:pal-python-starter
```
When Claude asks for details, supply:
- Table: CURATED.CUSTOMER_PROFILE, Key: CUSTOMER_ID, Target: IS_CHURNED
- Task: binary classification, Algorithm: GradientBoostingTree

Pass — all four must be true:
1. Connection uses `os.environ` — no hard-coded values.
2. Import: `from hana_ml.algorithms.pal.unified_classification import UnifiedClassification`
3. `.fit(data=train, label='IS_CHURNED', key='CUSTOMER_ID')` present.
4. No `<PLACEHOLDER>` tokens remain in the output.

---

## Release gate

| Stage | Check |
|-------|-------|
| 1 | Both `plugin validate` commands pass |
| 2 | Plugin and all 10 agents visible after `--plugin-dir` |
| 3 | Marketplace install succeeds; plugin visible after reload |
| 4 | `connection-doctor`, `landscape-recon`, `table-explorer`, `plugin-doctor` all return results |
| 5a | SELECT — no hook prompt |
| 5b | CREATE — confirmation prompt shown |
| 5c | DROP — hard-blocked, no prompt |
| 5d | DELETE without WHERE — hard-blocked |
| 5e | Multi-statement — hard-blocked |
| 6 | `pal-python-starter` output: env-var connection, correct import, fit call, no placeholders |

Do not release if any of 5b, 5c, 5d, or 5e fails.
