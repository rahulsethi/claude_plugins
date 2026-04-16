"""Example hana_ml starter for a HANA-based feature pipeline.

This file is intentionally conservative:
- connection settings come from environment variables
- the script reads a source feature table from HANA
- it shows where to save reviewed outputs back to a work schema
- it includes an optional PAL algorithm starter pattern

Adapt schema names, table names, key column, and label column for your project.
"""

from __future__ import annotations

import os
from typing import Optional

from hana_ml.dataframe import ConnectionContext


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


def main() -> None:
    source_schema = env("HANA_SOURCE_SCHEMA", env("HANA_SCHEMA", "CURATED"))
    work_schema = env("HANA_WORK_SCHEMA", "ML_WORK")
    feature_table = env("HANA_FEATURE_TABLE", "CUSTOMER_CHURN_FEATURES")
    key_col = env("HANA_FEATURE_KEY", "CUSTOMER_ID")
    label_col = env("HANA_LABEL_COL", "IS_CHURNED")

    cc = get_connection()
    try:
        df = cc.table(table=feature_table, schema=source_schema)
        print("Columns:", df.columns)
        print(df.head(5).collect())

        # Optional: save a reviewed copy into the work schema.
        # This is useful when the curated source schema should stay read-mostly.
        df.save(feature_table, schema=work_schema, force=True)
        print(f"Saved feature table copy to {work_schema}.{feature_table}")

        # Optional PAL starter.
        # Uncomment and adapt the algorithm you actually want to use.
        # Example shown here with RandomForestClassifier.
        # from hana_ml.algorithms.pal.ensemble import RandomForestClassifier
        #
        # train_df = cc.table(table=feature_table, schema=work_schema)
        # model = RandomForestClassifier(
        #     n_estimators=100,
        #     max_depth=8,
        #     thread_ratio=1.0,
        #     random_state=42,
        # )
        # model.fit(data=train_df, key=key_col, label=label_col)
        # scored = model.predict(data=train_df.drop(label_col), key=key_col)
        # scored.save("CUSTOMER_CHURN_SCORED", schema=work_schema, force=True)
        # print(f"Scored output saved to {work_schema}.CUSTOMER_CHURN_SCORED")

    finally:
        cc.close()


if __name__ == "__main__":
    main()
