---
name: score-date-design
description: Define entity grain, score date, prediction horizon, and leakage boundaries for an ML use case.
---

Sequence:
1. Confirm the scoring entity and grain: one row per what? (customer per month, order, machine per day)
2. Define the score date: the moment in time when the model runs and all feature values must already be known. This is not the event date of the target — it is the date the prediction is made.
3. Define the prediction horizon: how far ahead does the target event look? (e.g. churn within 30 days of score date, failure within 90 days)
4. Classify every candidate column into one of three categories:
   - SAFE — value is known on or before the score date (historical aggregation, prior-period status, stable attribute)
   - LEAKAGE — value is only known after the score date, or is directly derived from the target outcome (post-event cancel flag, target-period transaction sum, outcome status)
   - AMBIGUOUS — timestamp is unclear or the column may reflect post-score writes; treat as LEAKAGE until proven otherwise
5. Define history windows per feature type:
   - Recency: last event or status as-of the score date
   - Frequency: count or sum over a fixed lookback window anchored to the score date (e.g. 90-day window ending on score date)
   - Trend: ratio or slope comparing two non-overlapping windows both ending at or before the score date
   - Status / category: last known categorical value as-of the score date
6. Return a design note with four sections: **Grain**, **Score date definition**, **Target definition with horizon**, **Feature validity rules** (one rule per history window type, using column names from the source table).

Guardrails:
- Make all time boundaries explicit with actual column names, not just concepts.
- Flag AMBIGUOUS columns rather than classifying them as SAFE.
- Never use a column whose value is only knowable after the prediction event.
