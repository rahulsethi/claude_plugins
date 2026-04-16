---
name: training-split-planner
description: Design time-aware train, validation, and test splits for a HANA ML feature table.
---

Sequence:
1. Confirm: score date column name, prediction horizon, approximate row count, class balance (for classification), and task type (binary classification, regression, multiclass, time-series forecast).
2. Choose a split strategy:
   - **Chronological holdout** — most common for churn, propensity, and failure prediction. Sort by score date; oldest rows train, middle rows validate, newest rows test. Default proportions: 70% train / 15% validation / 15% test.
   - **Rolling origin** — for time-series forecasting where the model needs to be evaluated at multiple retrain points. Advance the training window forward, predict one step ahead each time.
   - **Grouped** — only when chronological order is not meaningful (cross-sectional or non-time-structured data).
3. Draft the split SQL using the score date column — never use `RAND()` or row numbers for time-structured data:
   ```sql
   SELECT
     <key_col>,
     <score_date_col>,
     <feature_cols>,
     <target_col>,
     CASE
       WHEN <score_date_col> < '<train_cutoff_date>'      THEN 'TRAIN'
       WHEN <score_date_col> < '<validation_cutoff_date>' THEN 'VALIDATION'
       ELSE                                                     'TEST'
     END AS SPLIT
   FROM <feature_table>
   ```
4. Verify split counts via `hana_execute_query`:
   ```sql
   SELECT SPLIT, COUNT(*) AS ROW_COUNT FROM (<split_select>) GROUP BY SPLIT ORDER BY SPLIT
   ```
   Confirm TRAIN has the most rows and TEST does not overlap with TRAIN dates.
5. Confirm label join: the target column must reflect an event that occurs after `score_date + prediction_horizon`. If the label is pre-joined in the feature table, verify the horizon is respected.
6. Return: split type chosen, date cutoffs, row counts per split, positive-class counts (for classification), and the split SQL or Python slice expression.

Guardrails:
- Never use `ORDER BY RAND()` or row-number splits for time-structured data.
- Minimum 200 positive examples in the TRAIN split for binary classification with PAL.
- Warn if the TEST split contains fewer than 50 positive examples — evaluation will be unreliable.
- For rolling-origin splits, document how many folds were used and the step size.
