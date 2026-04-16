---
name: star-schema-designer
description: Given a business question and a candidate HANA fact table, identify matching dimension tables, validate join integrity, and produce a star or snowflake schema design with explicit SQL and a Mermaid ER diagram.
---

Sequence:
1. Ask for: business question or analytical goal, candidate fact table name, schema_name.
2. Run `hana_describe_table` and `hana_explain_table` on the fact table. Identify:
   - **Grain**: what does one row represent? (one transaction, one event, one daily snapshot)
   - **Measure columns**: DECIMAL, DOUBLE, INTEGER columns with names containing AMOUNT, QTY, QUANTITY, VALUE, COUNT, PRICE, COST, REVENUE, DURATION — these are metrics to aggregate
   - **FK candidate columns**: INTEGER/BIGINT columns ending in _ID, _KEY, _NR, _CODE — these point to dimensions
   - **Date columns**: DATE/TIMESTAMP columns — these define time dimensions
3. For each FK candidate column, find the target dimension using this search:
   a. Check if `relationship-discoverer` output is available — use confirmed FK targets first.
   b. Otherwise, infer target from column name: if column is `CUSTOMER_ID`, look for tables named `CUSTOMER`, `CUSTOMER_MASTER`, `DIM_CUSTOMER`.
   c. Run `hana_list_tables` filtered by the root entity name.
   d. Run `hana_describe_table` on each candidate to confirm it looks like a dimension (< 500K rows, has CODE/NAME/DESCRIPTION pattern).
4. Validate join integrity for each fact → dimension pair (maxRows 1):
   ```sql
   SELECT
     COUNT(DISTINCT f.<fk_col>) AS FACT_DISTINCT_KEYS,
     COUNT(DISTINCT d.<pk_col>) AS DIM_DISTINCT_KEYS,
     SUM(CASE WHEN d.<pk_col> IS NULL THEN 1 ELSE 0 END) AS UNMATCHED_FACT_KEYS
   FROM "<schema>"."<fact_table>" f
   LEFT JOIN "<schema>"."<dim_table>" d ON f.<fk_col> = d.<pk_col>
   ```
   Flag if UNMATCHED_FACT_KEYS > 5% of FACT_DISTINCT_KEYS as REFERENTIAL_INTEGRITY_GAP.
5. Design the star schema:
   - **Center**: FACT table with grain definition, list of measures and FKs
   - **Spokes**: one DIMENSION per FK (labeled by role: Who=customer, What=product, Where=location, When=date, Why=reason)
   - **Snowflake extension**: if a dimension has further FK columns pointing to smaller lookup tables, note these as snowflake candidates
6. For the date column(s), recommend either:
   - Joining to an existing date dimension if one exists in the schema
   - Or using HANA date functions inline: `YEAR(<date_col>), MONTH(<date_col>), WEEK(<date_col>)`
7. Output:
   a. Mermaid ER diagram:
      ```
      erDiagram
        FACT_SALES {
          int CUSTOMER_ID FK
          int PRODUCT_ID FK
          date TRANSACTION_DATE
          decimal AMOUNT
        }
        DIM_CUSTOMER { int CUSTOMER_ID PK, string NAME }
        DIM_PRODUCT  { int PRODUCT_ID PK, string PRODUCT_NAME }
        FACT_SALES }o--|| DIM_CUSTOMER : "CUSTOMER_ID"
        FACT_SALES }o--|| DIM_PRODUCT  : "PRODUCT_ID"
      ```
   b. Reference SQL SELECT template with all joins and sample measure aggregations:
      ```sql
      SELECT
        d1.<label_col> AS CUSTOMER,
        d2.<label_col> AS PRODUCT,
        YEAR(f.TRANSACTION_DATE) AS YEAR,
        MONTH(f.TRANSACTION_DATE) AS MONTH,
        SUM(f.AMOUNT) AS TOTAL_REVENUE,
        COUNT(*) AS TRANSACTION_COUNT
      FROM "<schema>"."<fact_table>" f
      JOIN "<schema>"."<dim1>" d1 ON f.<fk1> = d1.<pk1>
      JOIN "<schema>"."<dim2>" d2 ON f.<fk2> = d2.<pk2>
      GROUP BY d1.<label_col>, d2.<label_col>,
               YEAR(f.TRANSACTION_DATE), MONTH(f.TRANSACTION_DATE)
      ORDER BY YEAR, MONTH
      ```
   c. Schema design document: `ROLE | TABLE | JOIN_COLUMN | JOIN_TYPE | INTEGRITY_STATUS | SNOWFLAKE_CANDIDATES`
8. Flag snowflake extension opportunities and ask if the user wants to drill down.
9. Offer to generate a CREATE VIEW for this star schema in the work schema via `reviewed-write-executor`.

Guardrails:
- Do not auto-classify a table as a dimension if its row count exceeds the fact table row count.
- Use LEFT JOIN for referential integrity check to expose unmatched keys — never INNER JOIN in validation.
- If UNMATCHED_FACT_KEYS > 5%, explicitly flag as a data quality issue before writing any view.
- Keep validation queries to maxRows 1 (aggregate only).
- This skill is read-only until the user explicitly requests a view be written.
