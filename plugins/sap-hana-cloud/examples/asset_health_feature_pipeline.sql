-- =============================================================================
-- Asset Health Failure Prediction — Feature Table Pipeline
-- =============================================================================
--
-- Use case:    Predict which industrial assets will fail within the next 30 days.
--              Scored monthly on the first day of each calendar month.
--
-- Grain:       One row per ASSET_ID per SCORE_DATE.
--
-- Score date:  First day of each calendar month (the moment the prediction runs).
--              All feature windows use data STRICTLY BEFORE this date.
--
-- Target:      FAILED_IN_NEXT_30D = 1 if the asset recorded a failure event
--              in [SCORE_DATE, SCORE_DATE + 30 days).
--              The target uses data AFTER the score date — this is intentional
--              and is NOT leakage, because the label is only known post-prediction.
--
-- Source tables (replace with your actual schema and table names):
--   CURATED.ASSET_MASTER        one row per asset; install date, type, manufacturer
--   CURATED.MAINTENANCE_EVENTS  maintenance and repair records per asset
--   CURATED.SENSOR_DAILY        daily aggregated sensor readings per asset
--   CURATED.FAILURE_EVENTS      asset failure records with FAILURE_DATE
--
-- Features (7 total, all leakage-safe):
--   ASSET_AGE_YEARS              stable attribute, computed from install date
--   DAYS_SINCE_LAST_MAINTENANCE  recency: days since last completed maintenance
--   MAINTENANCE_COUNT_90D        frequency: maintenance events in last 90 days
--   OVERDUE_MAINTENANCE_FLAG     1 if no maintenance in over 180 days
--   AVG_TEMPERATURE_30D          average sensor temperature in last 30 days
--   MAX_VIBRATION_30D            peak vibration reading in last 30 days
--   PRESSURE_TREND               avg pressure last 7 days / avg pressure days 8-30
--                                > 1.2 = rising; < 0.8 = dropping
--
-- Before running:
--   1. Run /sap-hana-cloud:write-safety-primer to confirm the write hook is active.
--   2. Run /sap-hana-cloud:feature-output-audit after creation to verify grain.
--   3. Replace WORK_SCHEMA with the value from ${user_config.work_schema}.
--   4. Adjust SCORE_DATE list in the score_dates CTE for your required periods.
--
-- This statement will be intercepted by the PreToolUse write hook and
-- presented for user confirmation before execution (write_mode = ask).
-- =============================================================================

CREATE TABLE WORK_SCHEMA.ASSET_HEALTH_FEATURES_20240601 AS
WITH

-- -------------------------------------------------------------------------
-- Score dates: one row per scoring period.
-- Extend this list or replace with a generated date series for your project.
-- -------------------------------------------------------------------------
score_dates AS (
    SELECT TO_DATE('2024-01-01') AS SCORE_DATE FROM DUMMY UNION ALL
    SELECT TO_DATE('2024-02-01')               FROM DUMMY UNION ALL
    SELECT TO_DATE('2024-03-01')               FROM DUMMY UNION ALL
    SELECT TO_DATE('2024-04-01')               FROM DUMMY UNION ALL
    SELECT TO_DATE('2024-05-01')               FROM DUMMY UNION ALL
    SELECT TO_DATE('2024-06-01')               FROM DUMMY
),

-- -------------------------------------------------------------------------
-- Asset-score grid: one row per (ASSET_ID, SCORE_DATE).
-- Includes stable attributes that are known at score time.
-- -------------------------------------------------------------------------
asset_score_grid AS (
    SELECT
        a.ASSET_ID,
        a.ASSET_TYPE,
        a.MANUFACTURER,
        a.INSTALL_DATE,
        sd.SCORE_DATE,
        -- ASSET_AGE_YEARS: stable attribute, cannot be leakage
        ROUND(DAYS_BETWEEN(a.INSTALL_DATE, sd.SCORE_DATE) / 365.25, 2)
            AS ASSET_AGE_YEARS
    FROM CURATED.ASSET_MASTER a
    CROSS JOIN score_dates sd
    WHERE a.INSTALL_DATE < sd.SCORE_DATE   -- asset must have existed before score date
),

-- -------------------------------------------------------------------------
-- Maintenance features (all windows close BEFORE score date)
-- -------------------------------------------------------------------------
maintenance_features AS (
    SELECT
        e.ASSET_ID,
        sd.SCORE_DATE,

        -- Recency: how many days since the last maintenance event
        DAYS_BETWEEN(
            MAX(CASE WHEN e.EVENT_DATE < sd.SCORE_DATE THEN e.EVENT_DATE END),
            sd.SCORE_DATE
        ) AS DAYS_SINCE_LAST_MAINTENANCE,

        -- Frequency: count of maintenance events in the 90-day window before score date
        COUNT(CASE
            WHEN e.EVENT_DATE >= ADD_DAYS(sd.SCORE_DATE, -90)
             AND e.EVENT_DATE  <  sd.SCORE_DATE
            THEN 1
        END) AS MAINTENANCE_COUNT_90D,

        -- Overdue flag: 1 if the last maintenance was more than 180 days ago
        CASE
            WHEN MAX(CASE WHEN e.EVENT_DATE < sd.SCORE_DATE THEN e.EVENT_DATE END)
                 < ADD_DAYS(sd.SCORE_DATE, -180)
            THEN 1
            ELSE 0
        END AS OVERDUE_MAINTENANCE_FLAG

    FROM CURATED.MAINTENANCE_EVENTS e
    CROSS JOIN score_dates sd
    GROUP BY e.ASSET_ID, sd.SCORE_DATE
),

-- -------------------------------------------------------------------------
-- Sensor features (all windows close BEFORE score date)
-- -------------------------------------------------------------------------
sensor_features AS (
    SELECT
        s.ASSET_ID,
        sd.SCORE_DATE,

        -- Average temperature over the 30-day window before score date
        AVG(CASE
            WHEN s.READING_DATE >= ADD_DAYS(sd.SCORE_DATE, -30)
             AND s.READING_DATE  <  sd.SCORE_DATE
            THEN s.AVG_TEMPERATURE
        END) AS AVG_TEMPERATURE_30D,

        -- Maximum vibration over the 30-day window before score date
        MAX(CASE
            WHEN s.READING_DATE >= ADD_DAYS(sd.SCORE_DATE, -30)
             AND s.READING_DATE  <  sd.SCORE_DATE
            THEN s.MAX_VIBRATION
        END) AS MAX_VIBRATION_30D,

        -- Pressure trend: average of last 7 days relative to days 8–30
        -- > 1.2 indicates rising pressure; < 0.8 indicates sustained drop
        AVG(CASE
            WHEN s.READING_DATE >= ADD_DAYS(sd.SCORE_DATE, -7)
             AND s.READING_DATE  <  sd.SCORE_DATE
            THEN s.AVG_PRESSURE
        END)
        / NULLIF(
            AVG(CASE
                WHEN s.READING_DATE >= ADD_DAYS(sd.SCORE_DATE, -30)
                 AND s.READING_DATE  <  ADD_DAYS(sd.SCORE_DATE, -7)
                THEN s.AVG_PRESSURE
            END),
        0) AS PRESSURE_TREND

    FROM CURATED.SENSOR_DAILY s
    CROSS JOIN score_dates sd
    GROUP BY s.ASSET_ID, sd.SCORE_DATE
),

-- -------------------------------------------------------------------------
-- Target label (data AFTER score date — not leakage, this is the future event)
-- -------------------------------------------------------------------------
failure_labels AS (
    SELECT
        f.ASSET_ID,
        sd.SCORE_DATE,
        MAX(CASE
            WHEN f.FAILURE_DATE >= sd.SCORE_DATE
             AND f.FAILURE_DATE  <  ADD_DAYS(sd.SCORE_DATE, 30)
            THEN 1
            ELSE 0
        END) AS FAILED_IN_NEXT_30D
    FROM CURATED.FAILURE_EVENTS f
    CROSS JOIN score_dates sd
    GROUP BY f.ASSET_ID, sd.SCORE_DATE
)

-- -------------------------------------------------------------------------
-- Final select: one row per (ASSET_ID, SCORE_DATE)
-- COALESCE defaults handle assets with no maintenance or sensor history
-- -------------------------------------------------------------------------
SELECT
    g.ASSET_ID,
    g.SCORE_DATE,
    g.ASSET_TYPE,
    g.MANUFACTURER,
    g.ASSET_AGE_YEARS,

    -- Maintenance features (default 999 days / 0 events / 1 overdue if no history)
    COALESCE(m.DAYS_SINCE_LAST_MAINTENANCE, 999) AS DAYS_SINCE_LAST_MAINTENANCE,
    COALESCE(m.MAINTENANCE_COUNT_90D,         0) AS MAINTENANCE_COUNT_90D,
    COALESCE(m.OVERDUE_MAINTENANCE_FLAG,      1) AS OVERDUE_MAINTENANCE_FLAG,

    -- Sensor features (NULL if no readings — audit with feature-output-audit)
    s.AVG_TEMPERATURE_30D,
    s.MAX_VIBRATION_30D,
    s.PRESSURE_TREND,

    -- Target label (0 if no failure recorded in the window)
    COALESCE(fl.FAILED_IN_NEXT_30D, 0) AS FAILED_IN_NEXT_30D

FROM asset_score_grid       g
LEFT JOIN maintenance_features m ON g.ASSET_ID = m.ASSET_ID AND g.SCORE_DATE = m.SCORE_DATE
LEFT JOIN sensor_features      s ON g.ASSET_ID = s.ASSET_ID AND g.SCORE_DATE = s.SCORE_DATE
LEFT JOIN failure_labels       fl ON g.ASSET_ID = fl.ASSET_ID AND g.SCORE_DATE = fl.SCORE_DATE;

-- =============================================================================
-- Post-creation checks (run manually via /sap-hana-cloud:feature-output-audit):
--
--   SELECT COUNT(*), COUNT(DISTINCT ASSET_ID || '|' || SCORE_DATE)
--   FROM WORK_SCHEMA.ASSET_HEALTH_FEATURES_20240601;
--   -- TOTAL and UNIQUE should be equal (one row per asset per score date)
--
--   SELECT SCORE_DATE, COUNT(*) AS ASSETS, SUM(FAILED_IN_NEXT_30D) AS FAILURES
--   FROM WORK_SCHEMA.ASSET_HEALTH_FEATURES_20240601
--   GROUP BY SCORE_DATE
--   ORDER BY SCORE_DATE;
--   -- Failure rate should be believable (typically 1–10% for asset health tasks)
-- =============================================================================
