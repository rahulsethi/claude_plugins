---
name: feature-set-planner
description: Design a leakage-aware ML feature set from curated HANA tables.
---

Sequence:
1. Confirm inputs: grain (one row per what), score date column or value, target label column and prediction horizon, source tables from `curated-dataset-recon` or user input.
2. For each source table call `hana_describe_table` and `hana_explain_table` to get columns and semantic notes.
3. Identify structural columns: primary key, foreign keys, event timestamps. These are not features — label them STRUCTURAL.
4. Classify every remaining column for leakage risk:
   - SAFE: value is known at score time (prior-period aggregate, stable attribute, historical categorical)
   - LEAKAGE: value is only known after the score date or correlates directly with the target (e.g. outcome flag, post-event cancel date, target-period revenue, churn label itself)
   - AMBIGUOUS: update timestamp is unclear; treat as LEAKAGE unless the user confirms otherwise
5. For SAFE columns, propose features with explicit aggregation logic:
   - Recency: `DAYS_BETWEEN(MAX(<event_date>), <score_date>)`
   - Frequency: `COUNT(*) OVER last <N> days`
   - Monetary / intensity: `SUM(<amount>) OVER last <N> days`
   - Trend: `SUM last 30 days / NULLIF(SUM days 31-90, 0)`
   - Status: `LAST_VALUE(<status_col>) as-of score date`
6. Return a feature plan table with one row per proposed feature: `feature_name | source_table | aggregation_logic | lookback_window | leakage_risk | rationale`.
7. Recommend materialization target `${user_config.work_schema}` and hand off to `feature-table-materializer`.

Guardrails:
- Reject LEAKAGE features. Describe AMBIGUOUS features only as advisory with an explicit warning.
- Do not propose features with an expected null rate above 80% unless the user provides a business reason.
- All lookback windows must be anchored to the score date column, not to the wall-clock date of the query.
