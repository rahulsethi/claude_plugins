# Changelog

## 0.2.0-alpha.1
- Added 5 ontology and knowledge graph skills: `relationship-discoverer`, `entity-classifier`, `ontology-planner`, `knowledge-graph-builder`, `column-cross-mapper`
- `knowledge-graph-builder` materializes HANA-native property graph (VERTICES + EDGES) and RDF triple store (TRIPLES) in work schema with full SPARQL 1.1 compatibility
- Knowledge graph supports three query modes: SQL on TRIPLES (always available), HANA Graph Service REST/SPARQL endpoint, and HANA GRAPH WORKSPACE (property graph)
- Added 3 view and lineage skills: `view-explorer`, `procedure-catalog`, `lineage-graph`
- Added 3 extended profiling skills: `full-schema-profiler`, `temporal-coverage-scan`, `distribution-analyzer`
- Added 3 BI design skills: `star-schema-designer`, `kpi-mapper`, `data-freshness-dashboard`
- Added 3 new agents: `hana-ontologist` (ontology pipeline), `hana-data-cataloger` (full schema catalog), `hana-bi-architect` (BI layer design)
- Total: 44 skills, 13 agents

## 0.1.0-alpha.1
- Recreated scaffold with read and write workflows
- Added write guard hook for `hana_execute_query`
- Improved 10 ML/PAL skills with concrete SQL, leakage criteria, and code skeletons
- Added asset health feature pipeline example (SQL + Python hana_ml)
- Updated README with beginner-friendly write-mode and first-tests sections
- Expanded skills and agents for reviewed DDL/DML and `hana_ml` / PAL planning
- Added continuation pack, project hook example, semantics JSON example, and Python starter assets
