---
name: pal-python-starter
description: Generate a Python hana_ml starter script for a PAL algorithm or dataframe workflow.
---

Sequence:
1. Confirm: feature table name, schema, key column, target column (supervised tasks), task type (binary classification, regression, clustering, time-series, or pure dataframe).
2. Ask which algorithm — or recommend based on task type:
   - Binary / multiclass classification: `UnifiedClassification(func='GradientBoostingTree')` — best default
   - Regression: `UnifiedRegression(func='GradientBoostingTree')`
   - Clustering: `KMeans` or `DBSCAN`
   - Time-series: `AutoARIMA` or `ExponentialSmoothing`
   - Pure dataframe (no PAL): use `hana_ml.dataframe.ConnectionContext` and `.collect()` to pull to pandas
3. Generate the script with this structure — fill in the confirmed values, do not leave placeholder comments:

   ```python
   import os
   from hana_ml import ConnectionContext
   # adjust import per task type:
   from hana_ml.algorithms.pal.unified_classification import UnifiedClassification

   # Connection — set these env vars before running:
   # HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD
   cc = ConnectionContext(
       address=os.environ['HANA_HOST'],
       port=int(os.environ['HANA_PORT']),
       user=os.environ['HANA_USER'],
       password=os.environ['HANA_PASSWORD'],
       encrypt=True,
   )

   df = cc.table('<TABLE>', schema='<SCHEMA>')

   # Split assumes a SPLIT column from training-split-planner
   train = df.filter("SPLIT = 'TRAIN'")
   test  = df.filter("SPLIT = 'TEST'")

   model = UnifiedClassification(func='GradientBoostingTree')
   model.fit(train, label='<TARGET_COL>', key='<KEY_COL>')

   predictions = model.predict(test, key='<KEY_COL>')
   print(predictions.collect().head(10))

   # Feature importance (if supported by the algorithm)
   print(model.feature_importances_.collect())
   ```

4. If the feature table has a SPLIT column from `training-split-planner`, reference it directly as shown above. If not, add a comment pointing to `training-split-planner`.
5. If PAL role access is unconfirmed, add a comment at the top: `# Run /sap-hana-cloud:pal-role-checker to verify PAL access before executing`.
6. If the feature table does not exist yet, say so and point to `feature-table-materializer` before generating the script.

Guardrails:
- Never hard-code passwords or connection strings.
- Use `encrypt=True` by default unless the user explicitly says SSL is off.
- Keep the generated script self-contained — no project-specific imports beyond `hana_ml` and `os`.
- Replace all `<PLACEHOLDER>` values with the confirmed names before returning the script.
