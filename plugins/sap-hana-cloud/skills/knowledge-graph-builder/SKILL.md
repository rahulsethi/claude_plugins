---
name: knowledge-graph-builder
description: Build a HANA-native knowledge graph from schema discovery results. Creates a property graph (VERTEX + EDGE tables for HANA GRAPH queries) and an RDF triple store (TRIPLES table for SPARQL 1.1 queries) — both materialized in the configured work schema. Generates GRAPH WORKSPACE DDL and sample SPARQL queries.
---

Prerequisites:
- `relationship-discoverer` output (edge list with CONFIRMED + INFERRED relationships)
- `entity-classifier` output (table classification table)
- `ontology-planner` output (namespace definitions, OWL class + property mappings)
- `write_mode` set to `ask` or `allow` in plugin config
- `work_schema` configured in plugin config

If any prerequisite is missing, run those skills first before proceeding.

Sequence:

## Phase 1 — Confirm targets
1. Restate to the user:
   - Source schema: `<schema>`
   - Vertex table target: `"<work_schema>"."KG_<SCHEMA>_VERTICES"`
   - Edge table target: `"<work_schema>"."KG_<SCHEMA>_EDGES"`
   - Triple store target: `"<work_schema>"."KG_<SCHEMA>_TRIPLES"`
   - Graph workspace name: `KG_<SCHEMA>` (to be created by user with DBA role)
   Confirm with user before any write.

## Phase 2 — Create property graph tables (reviewed writes via write guard)
2. Create VERTEX table:
   ```sql
   CREATE TABLE "<work_schema>"."KG_<SCHEMA>_VERTICES" (
     VERTEX_ID    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
     NODE_IRI     NVARCHAR(2000) NOT NULL,
     NODE_TYPE    NVARCHAR(100),
     TABLE_NAME   NVARCHAR(256),
     SCHEMA_NAME  NVARCHAR(256),
     ENTITY_TYPE  NVARCHAR(50),
     ROW_COUNT    BIGINT,
     COLUMN_COUNT INTEGER,
     LABEL        NVARCHAR(500),
     CREATED_AT   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```
3. Create EDGE table:
   ```sql
   CREATE TABLE "<work_schema>"."KG_<SCHEMA>_EDGES" (
     EDGE_ID           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
     SOURCE_VERTEX_ID  BIGINT NOT NULL,
     TARGET_VERTEX_ID  BIGINT NOT NULL,
     RELATIONSHIP_TYPE NVARCHAR(100),
     PREDICATE_IRI     NVARCHAR(2000),
     CONFIDENCE        NVARCHAR(20),
     CONSTRAINT_NAME   NVARCHAR(256),
     SOURCE_COLUMN     NVARCHAR(256),
     TARGET_COLUMN     NVARCHAR(256),
     LABEL             NVARCHAR(500)
   )
   ```

## Phase 3 — Create RDF triple store (for SPARQL)
4. Create TRIPLES table (SPARQL-queryable via HANA Graph Service or SQL):
   ```sql
   CREATE TABLE "<work_schema>"."KG_<SCHEMA>_TRIPLES" (
     TRIPLE_ID  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
     SUBJECT    NVARCHAR(2000) NOT NULL,
     PREDICATE  NVARCHAR(2000) NOT NULL,
     OBJECT     NVARCHAR(4000) NOT NULL,
     GRAPH_URI  NVARCHAR(2000) DEFAULT 'http://sap.com/hana/kg/<schema>',
     IS_LITERAL TINYINT DEFAULT 0,
     DATATYPE   NVARCHAR(200),
     LANG_TAG   NVARCHAR(20)
   )
   ```
5. Create an index on SUBJECT for efficient SPARQL subject lookups:
   ```sql
   CREATE INDEX "KG_<SCHEMA>_TRIPLES_SUBJ_IDX"
     ON "<work_schema>"."KG_<SCHEMA>_TRIPLES" (SUBJECT)
   ```
6. Create an index on PREDICATE for efficient predicate filtering:
   ```sql
   CREATE INDEX "KG_<SCHEMA>_TRIPLES_PRED_IDX"
     ON "<work_schema>"."KG_<SCHEMA>_TRIPLES" (PREDICATE)
   ```

## Phase 4 — Populate VERTICES
7. Build INSERT statements from entity-classifier results (batch max 50 rows per INSERT):
   ```sql
   INSERT INTO "<work_schema>"."KG_<SCHEMA>_VERTICES"
     (NODE_IRI, NODE_TYPE, TABLE_NAME, SCHEMA_NAME, ENTITY_TYPE, ROW_COUNT, COLUMN_COUNT, LABEL)
   VALUES
     ('http://sap.com/hana/schema/<schema>#<TABLE_NAME>', 'hana:FactTable',
      '<TABLE_NAME>', '<schema>', 'FACT', <ROW_COUNT>, <COLUMN_COUNT>, '<TABLE_NAME>'),
     -- repeat for each classified table
   ```

## Phase 5 — Populate EDGES
8. INSERT confirmed FK edges first (SOURCE_VERTEX_ID from VERTICES):
   ```sql
   INSERT INTO "<work_schema>"."KG_<SCHEMA>_EDGES"
     (SOURCE_VERTEX_ID, TARGET_VERTEX_ID, RELATIONSHIP_TYPE, PREDICATE_IRI,
      CONFIDENCE, CONSTRAINT_NAME, SOURCE_COLUMN, TARGET_COLUMN, LABEL)
   VALUES
     (<src_id>, <tgt_id>, 'FOREIGN_KEY',
      'http://sap.com/hana/ontology#hasForeignKey',
      'CONFIRMED', '<CONSTRAINT_NAME>', '<SOURCE_COL>', '<TARGET_COL>',
      '<SRC_TABLE> → <TGT_TABLE> via <COL>'),
     -- repeat
   ```
9. INSERT inferred (naming-pattern) edges:
   ```sql
   -- same shape, RELATIONSHIP_TYPE = 'INFERRED', CONFIDENCE = 'MEDIUM' or 'LOW'
   ```

## Phase 6 — Populate RDF TRIPLES
10. INSERT ontology TBox triples (class hierarchy, one batch per entity type):
    ```sql
    -- rdf:type assertions for each table node
    INSERT INTO "<work_schema>"."KG_<SCHEMA>_TRIPLES"
      (SUBJECT, PREDICATE, OBJECT, IS_LITERAL)
    VALUES
      ('http://sap.com/hana/schema/<schema>#<TABLE>',
       'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
       'http://sap.com/hana/ontology#FactTable', 0),
      -- rdfs:label
      ('http://sap.com/hana/schema/<schema>#<TABLE>',
       'http://www.w3.org/2000/01/rdf-schema#label',
       '<TABLE>', 1),
      -- hana:rowCount as literal
      ('http://sap.com/hana/schema/<schema>#<TABLE>',
       'http://sap.com/hana/ontology#rowCount',
       '<ROW_COUNT>', 1),
      -- repeat for all tables
    ```
11. INSERT relationship triples (object properties):
    ```sql
    INSERT INTO "<work_schema>"."KG_<SCHEMA>_TRIPLES"
      (SUBJECT, PREDICATE, OBJECT, IS_LITERAL)
    VALUES
      ('http://sap.com/hana/schema/<schema>#<SOURCE_TABLE>',
       'http://sap.com/hana/ontology#relatesTo',
       'http://sap.com/hana/schema/<schema>#<TARGET_TABLE>', 0),
      ('http://sap.com/hana/schema/<schema>#<SOURCE_TABLE>',
       'http://sap.com/hana/ontology#relationshipType',
       'FOREIGN_KEY', 1),
      -- repeat for all edges
    ```

## Phase 7 — Postchecks
12. Verify counts (read-only queries):
    ```sql
    SELECT 'VERTICES' AS TYPE, COUNT(*) AS CNT FROM "<work_schema>"."KG_<SCHEMA>_VERTICES"
    UNION ALL
    SELECT 'EDGES', COUNT(*) FROM "<work_schema>"."KG_<SCHEMA>_EDGES"
    UNION ALL
    SELECT 'TRIPLES', COUNT(*) FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES"
    ```

## Phase 8 — HANA GRAPH WORKSPACE DDL (display only — requires DBA role)
13. Present this DDL for the user to run manually with a DBA or GRAPH ADMIN-privileged account:
    ```sql
    -- Run this with DBA or GRAPH ADMIN privilege to enable HANA GRAPH queries
    CREATE GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
      EDGE TABLE "<work_schema>"."KG_<SCHEMA>_EDGES"
        SOURCE COLUMN "SOURCE_VERTEX_ID"
        TARGET COLUMN "TARGET_VERTEX_ID"
        KEY COLUMN "EDGE_ID"
      VERTEX TABLE "<work_schema>"."KG_<SCHEMA>_VERTICES"
        KEY COLUMN "VERTEX_ID";
    ```

## Phase 9 — SPARQL query templates
14. Output ready-to-use SPARQL queries with three execution options:

    **Option A — SQL on TRIPLES table (always available, no Graph Engine needed):**
    ```sql
    -- Find all entity types
    SELECT SUBJECT, OBJECT AS ENTITY_TYPE
    FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES"
    WHERE PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
      AND IS_LITERAL = 0;

    -- Find all relationships between tables
    SELECT S.OBJECT AS SOURCE_TYPE, T.OBJECT AS TARGET_TYPE,
           R.OBJECT AS RELATIONSHIP_TYPE
    FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES" S
    JOIN "<work_schema>"."KG_<SCHEMA>_TRIPLES" R
      ON S.SUBJECT = R.SUBJECT AND R.PREDICATE = 'http://sap.com/hana/ontology#relatesTo'
    JOIN "<work_schema>"."KG_<SCHEMA>_TRIPLES" T
      ON T.SUBJECT = R.SUBJECT AND T.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    WHERE S.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';

    -- Find all FACT tables
    SELECT SUBJECT AS TABLE_IRI
    FROM "<work_schema>"."KG_<SCHEMA>_TRIPLES"
    WHERE PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
      AND OBJECT = 'http://sap.com/hana/ontology#FactTable';
    ```

    **Option B — SPARQL 1.1 via HANA Graph Service REST API (requires Graph Engine enabled):**
    ```sparql
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX hana: <http://sap.com/hana/ontology#>

    # Find all entities and their types
    SELECT ?entity ?type WHERE {
      ?entity rdf:type ?type .
      FILTER(STRSTARTS(STR(?type), "http://sap.com/hana/ontology#"))
    }

    # Find all direct relationships
    SELECT ?source ?target ?relType WHERE {
      ?source hana:relatesTo ?target .
      ?source hana:relationshipType ?relType .
    }

    # Find all tables connected to a given table (1-hop neighbourhood)
    SELECT ?neighbour ?relType WHERE {
      <http://sap.com/hana/schema/<schema>#<TABLE>> hana:relatesTo ?neighbour .
      <http://sap.com/hana/schema/<schema>#<TABLE>> hana:relationshipType ?relType .
    }

    # CONSTRUCT: materialize a subgraph as RDF
    CONSTRUCT {
      ?s hana:relatesTo ?o .
    }
    WHERE {
      ?s rdf:type hana:FactTable .
      ?s hana:relatesTo ?o .
    }
    ```

    **Option C — HANA GRAPH query on property graph (after GRAPH WORKSPACE is created):**
    ```sql
    -- Traverse all 1-hop relationships from a given node
    GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
    MATCH (src)-[e]->(tgt)
    WHERE src.TABLE_NAME = '<table>'
    RETURN src.TABLE_NAME AS SOURCE, e.RELATIONSHIP_TYPE, tgt.TABLE_NAME AS TARGET;

    -- Find all FACT table nodes
    GRAPH WORKSPACE "<work_schema>"."KG_<SCHEMA>"
    MATCH (v)
    WHERE v.ENTITY_TYPE = 'FACT'
    RETURN v.TABLE_NAME, v.ROW_COUNT;
    ```

15. Output a Mermaid ER diagram of the discovered graph for immediate visualization:
    ```
    erDiagram
        FACT_TABLE_A ||--o{ DIMENSION_B : "FK_COL"
        FACT_TABLE_A ||--o{ MASTER_C : "inferred"
        ...
    ```

## Phase 10 — HANA Graph Service connection note
16. Explain how to connect the SPARQL endpoint:
    - HANA Cloud Graph Service REST endpoint: `https://<host>/v1/query/<tenant>/graphs/KG_<SCHEMA>/sparql`
    - Method: POST, Content-Type: application/sparql-query, Accept: application/sparql-results+json
    - Authentication: same HANA credentials (basic auth or OAuth)
    - This requires the Graph Engine feature to be provisioned in the HANA Cloud instance
    - If Graph Engine is not available, use **Option A** (SQL on TRIPLES table) — it provides equivalent query power via standard SQL

Guardrails:
- Every CREATE TABLE and INSERT must go through `hana_execute_query` and the write guard. Never bypass.
- Prefix ALL table names with work_schema. Never write into source data schemas.
- Batch INSERT statements to max 50 value rows each to stay within SQL length limits.
- The GRAPH WORKSPACE DDL is display-only — present as a code block, do not execute it (requires DBA privilege).
- If `work_schema` is not configured, halt immediately and redirect to `work-schema-bootstrap`.
- If postchecks show 0 rows in VERTICES, the INSERT phase failed — diagnose before proceeding.
- Inferred edges must always carry `CONFIDENCE = 'MEDIUM'` or `'LOW'` — never promote them to CONFIRMED without user validation.
- This skill creates permanent tables in the work schema. Remind user that cleanup requires DROP TABLE with write guard approval.
