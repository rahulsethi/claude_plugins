"""Asset health failure prediction using hana_ml.

Use case:
    Predict which industrial assets will fail within the next 30 days.
    Scored monthly at the first day of each calendar month.

Grain:
    One row per ASSET_ID per SCORE_DATE.

Source table:
    WORK_SCHEMA.ASSET_HEALTH_FEATURES_YYYYMMDD
    Created by examples/asset_health_feature_pipeline.sql.

Split strategy:
    Chronological holdout — train on older score dates, test on the most recent.
    Never use random splits for time-structured data.

Algorithm:
    UnifiedClassification(func='GradientBoostingTree') — a good default for
    binary failure prediction. Swap func= for 'RandomForest' or 'LogisticRegression'
    if your data volume or PAL version requires it.

Prerequisites:
    - Feature table materialized via /sap-hana-cloud:reviewed-write-executor
    - PAL access confirmed via /sap-hana-cloud:pal-preflight
    - pip install hana-ml

Environment variables:
    HANA_HOST            HANA Cloud SQL endpoint hostname
    HANA_PORT            SQL port (default: 443 for HANA Cloud)
    HANA_USER            Technical HANA user
    HANA_PASSWORD        Password for the technical user
    HANA_WORK_SCHEMA     Schema containing the feature table (default: ML_WORK)
    HANA_FEATURE_TABLE   Feature table name (default: ASSET_HEALTH_FEATURES_20240601)
"""

from __future__ import annotations

import os
from typing import Optional

from hana_ml import ConnectionContext
from hana_ml.algorithms.pal.unified_classification import UnifiedClassification


# ---------------------------------------------------------------------------
# Feature and label definitions — keep in sync with the SQL pipeline
# ---------------------------------------------------------------------------
KEY_COL   = "ASSET_ID"
LABEL_COL = "FAILED_IN_NEXT_30D"
SCORE_DATE_COL = "SCORE_DATE"

# Categorical columns: HANA PAL needs these declared explicitly
CATEGORICAL_COLS = ["ASSET_TYPE", "MANUFACTURER", "OVERDUE_MAINTENANCE_FLAG"]

# Chronological split cutoffs — adjust to match your score_dates CTE
# train:      SCORE_DATE <  TRAIN_CUTOFF
# validation: SCORE_DATE >= TRAIN_CUTOFF and < VAL_CUTOFF
# test:       SCORE_DATE >= VAL_CUTOFF
TRAIN_CUTOFF = "2024-04-01"
VAL_CUTOFF   = "2024-06-01"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_connection() -> ConnectionContext:
    return ConnectionContext(
        address=env("HANA_HOST"),
        port=int(env("HANA_PORT", "443")),
        user=env("HANA_USER"),
        password=env("HANA_PASSWORD"),
        encrypt=env("HANA_ENCRYPT", "true").lower() == "true",
        sslValidateCertificate=env("HANA_VALIDATE_CERT", "true").lower() == "true",
    )


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    work_schema   = env("HANA_WORK_SCHEMA",   "ML_WORK")
    feature_table = env("HANA_FEATURE_TABLE", "ASSET_HEALTH_FEATURES_20240601")
    scored_table  = feature_table.replace("FEATURES", "SCORED")

    cc = get_connection()
    try:
        df = cc.table(table=feature_table, schema=work_schema)
        print(f"Feature table : {work_schema}.{feature_table}")
        print(f"Columns       : {df.columns}")
        print(f"Total rows    : {df.count()}")

        # --- Chronological train / validation / test split -------------------
        # Anchor splits to SCORE_DATE, not to row order or RAND().
        train = df.filter(f"{SCORE_DATE_COL} <  '{TRAIN_CUTOFF}'")
        val   = df.filter(
            f"{SCORE_DATE_COL} >= '{TRAIN_CUTOFF}' AND {SCORE_DATE_COL} < '{VAL_CUTOFF}'"
        )
        test  = df.filter(f"{SCORE_DATE_COL} >= '{VAL_CUTOFF}'")

        print(f"\nTrain rows      : {train.count()}")
        print(f"Validation rows : {val.count()}")
        print(f"Test rows       : {test.count()}")

        # Check class balance in training data before fitting
        # PAL needs at least ~200 positive examples for stable GBT training
        label_dist = train.agg(
            [("count", LABEL_COL, "N")],
            group_by=[LABEL_COL],
        )
        print("\nLabel distribution in train split:")
        print(label_dist.collect())

        # --- Train -----------------------------------------------------------
        model = UnifiedClassification(
            func="GradientBoostingTree",
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            min_sample_weight_leaf=5,
            random_state=42,
        )

        model.fit(
            data=train,
            key=KEY_COL,
            label=LABEL_COL,
            categorical_variable=CATEGORICAL_COLS,
        )
        print("\nTraining complete.")

        # --- Evaluate on validation split ------------------------------------
        val_preds = model.predict(data=val, key=KEY_COL)
        print("\nValidation predictions (first 10 rows):")
        print(val_preds.collect().head(10))

        # --- Feature importance ----------------------------------------------
        print("\nFeature importances:")
        print(model.feature_importances_.collect())

        # --- Score the test split and save to work schema --------------------
        test_preds = model.predict(data=test, key=KEY_COL)
        test_preds.save(where=(work_schema, scored_table), force=True)
        print(f"\nTest predictions saved to {work_schema}.{scored_table}")

        # --- Quick failure-rate sanity check on test predictions -------------
        # SCORE should be the predicted probability of failure (class 1)
        high_risk = test_preds.filter("SCORE > 0.5").count()
        total     = test_preds.count()
        print(
            f"\nHigh-risk assets (predicted probability > 0.5): "
            f"{high_risk} of {total} "
            f"({100 * high_risk / max(total, 1):.1f}%)"
        )

    finally:
        cc.close()


if __name__ == "__main__":
    main()
