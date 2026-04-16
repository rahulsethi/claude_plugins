---
name: hana-ml-feature-flow
description: Orchestrate the full planning and build flow from source-table discovery to a ready Python hana_ml starter.
---

This is an orchestration skill. It invokes other skills in sequence, tracks what has been confirmed at each step, and surfaces decision points rather than running blindly to the end.

Step sequence:

**Step 1 — Discover source tables** → invoke `curated-dataset-recon`
- Output to carry forward: table name, schema, key column, event date column, suggested role (label / feature source).
- Decision: if fewer than 2 candidates are found, pause and ask the user to provide table names directly before continuing.

**Step 2 — Define the ML problem** → invoke `score-date-design`
- Output to carry forward: grain, score date definition, target column, prediction horizon, leakage boundary.
- Decision: do not proceed to feature design until the user confirms the leakage boundary. An unclear boundary now causes wasted materialization later.

**Step 3 — Design features** → invoke `feature-set-planner`
- Output to carry forward: feature plan table (feature_name, source, aggregation, window, leakage_risk).
- Decision: discard all LEAKAGE features before continuing. Flag AMBIGUOUS features for user review — do not include them without explicit approval.

**Step 4 — Check environment** → invoke `pal-preflight`
- Output to carry forward: READY / PARTIAL / BLOCKED and the specific reason.
- Decision:
  - BLOCKED on connection or missing work schema → stop here and resolve before materializing.
  - BLOCKED on PAL installation or roles → continue but note that the Python starter will use hana_ml lightweight mode, not PAL stored procedures.
  - PARTIAL → continue with the caveat documented.

**Step 5 — Materialize the feature table** → invoke `feature-table-materializer`
- Output to carry forward: table name in `${user_config.work_schema}`, confirmed row count, grain check passed.
- Decision: skip this step only if the user confirms they will pass the feature SELECT directly to `hana_ml` without materializing (acceptable for small exploratory work).

**Step 6 — Audit the feature table** → invoke `feature-output-audit`
- Output to carry forward: audit verdict and list of any HIGH NULL / CONSTANT / BLOCKED issues.
- Decision: if verdict is REVIEW NEEDED, surface the specific columns and ask the user whether to fix and re-materialize or proceed with caveats. If BLOCKED, stop — do not generate a Python starter against a broken table.

**Step 7 — Design splits** → invoke `training-split-planner`
- Output to carry forward: split type, date cutoffs or SPLIT column, row counts per split.

**Step 8 — Generate Python starter** → invoke `pal-python-starter`
- Output: self-contained Python script with connection, HANA dataframe, train/test split, fit, predict, and feature importance.

Return a project summary at the end:
- Source tables used
- Feature table name and row count
- Split strategy and cutoff dates
- Any caveats (PAL role gaps, HIGH NULL features, AMBIGUOUS features included by user decision)
- The generated Python script inline or as a named artifact
