---
name: ontology-planner
description: Produce a structured OWL/RDF ontology from HANA schema discovery results. Maps tables to OWL classes, columns to datatype/object properties, and relationships to OWL object properties. Output is Turtle (.ttl) + JSON-LD context ready for HANA knowledge graph materialization.
---

Prerequisites: Run `relationship-discoverer` and `entity-classifier` first. Have their outputs available in the conversation.

Sequence:
1. Confirm inputs with user: schema_name, entity classification table (from entity-classifier), relationship edge list (from relationship-discoverer). If these are not available, run those skills first.
2. Define ontology namespaces:
   ```
   @prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix owl:   <http://www.w3.org/2002/07/owl#> .
   @prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
   @prefix hana:  <http://sap.com/hana/ontology#> .
   @prefix hanat: <http://sap.com/hana/schema/<SCHEMA_NAME>#> .
   ```
3. Map each entity type to an OWL class hierarchy:
   - All tables → subclass of `hana:DatabaseTable`
   - FACT tables → `hana:FactTable rdfs:subClassOf hana:DatabaseTable`
   - DIMENSION tables → `hana:DimensionTable rdfs:subClassOf hana:DatabaseTable`
   - MASTER tables → `hana:MasterDataTable rdfs:subClassOf hana:DatabaseTable`
   - REFERENCE tables → `hana:ReferenceTable rdfs:subClassOf hana:DatabaseTable`
   - STAGING tables → `hana:StagingTable rdfs:subClassOf hana:DatabaseTable`
   - ANALYTICAL tables → `hana:AnalyticalTable rdfs:subClassOf hana:DatabaseTable`
4. For each table, run `hana_describe_table` and `hana_explain_table` to get column-level details and any existing semantic overlay.
5. Map each column to an ontology property type:
   - INTEGER/BIGINT primary-key column → `owl:InverseFunctionalProperty` (unique entity identifier)
   - FK column (confirmed from relationship-discoverer) → `owl:ObjectProperty` with `rdfs:range` pointing to referenced table's class
   - DATE / TIMESTAMP / SECONDDATE column → `owl:DatatypeProperty` with `rdfs:range xsd:date` or `xsd:dateTime`
   - DECIMAL / DOUBLE / FLOAT measure column → `owl:DatatypeProperty` with `rdfs:range xsd:decimal`
   - VARCHAR/NVARCHAR column with name containing STATUS, TYPE, CODE, FLAG → `owl:DatatypeProperty` tagged as `hana:categoricalProperty`
   - VARCHAR/NVARCHAR text column → `owl:DatatypeProperty` with `rdfs:range xsd:string`
6. Map relationships to OWL object properties:
   - CONFIRMED FK edge → `hanat:<source_table>_<col> a owl:ObjectProperty ; rdfs:domain hanat:<source_table> ; rdfs:range hanat:<target_table> ; hana:inferenceType "foreign-key" .`
   - INFERRED edge → same structure but `hana:inferenceType "naming-pattern" ; hana:confidence "medium" .`
   - Add `owl:inverseOf` annotation where the inverse relationship is semantically meaningful.
7. Generate three output artifacts:
   a. **Turtle (.ttl) ontology** — TBox only (schema-level classes and properties, no instance data)
   b. **JSON-LD @context block** — maps table/column names to IRI namespace for embedding with query results
   c. **Human-readable summary table**: `ENTITY | OWL_CLASS | KEY_PROPERTIES | OBJECT_PROPERTIES | DATATYPE_PROPERTIES`
8. Note any tables/columns skipped due to insufficient metadata and recommend `semantics-bootstrap` to fill gaps.
9. Offer to hand off to `knowledge-graph-builder` to materialize this ontology as HANA-queryable tables and RDF triple store.

Guardrails:
- Output is TBox only. ABox (instance-level data) is the responsibility of knowledge-graph-builder.
- Do not enumerate all column values for `owl:oneOf` unless `hana_execute_query` confirms cardinality < 20 and row count < 500.
- If `hana_explain_table` returns no semantic overlay, mark those columns as ANNOTATION_MISSING and continue — do not block.
- Turtle output should be valid and parseable — validate namespace prefix consistency before returning.
- This skill is read-only. No HANA writes are performed.
