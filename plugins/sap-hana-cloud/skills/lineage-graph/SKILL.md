---
name: lineage-graph
description: Trace object dependencies upstream and downstream for a HANA table or view using SYS.OBJECT_DEPENDENCIES. Produces a Mermaid flowchart showing what feeds the object and what consumes it. Up to 3 levels deep.
---

Sequence:
1. Ask for: schema_name, object_name, object_type (TABLE or VIEW), and direction:
   - UP → what feeds this object (upstream sources)
   - DOWN → what this object feeds (downstream consumers)
   - BOTH → full neighbourhood (default)
2. Run UPSTREAM query — what does this object depend on (maxRows 100):
   ```sql
   SELECT DEPENDENT_SCHEMA_NAME, DEPENDENT_OBJECT_NAME, DEPENDENT_OBJECT_TYPE,
          BASE_SCHEMA_NAME, BASE_OBJECT_NAME, BASE_OBJECT_TYPE,
          DEPENDENCY_TYPE
   FROM SYS.OBJECT_DEPENDENCIES
   WHERE DEPENDENT_SCHEMA_NAME = '<schema>'
     AND DEPENDENT_OBJECT_NAME = '<object>'
   ORDER BY BASE_OBJECT_TYPE, BASE_OBJECT_NAME
   ```
3. Run DOWNSTREAM query — what depends on this object (maxRows 100):
   ```sql
   SELECT DEPENDENT_SCHEMA_NAME, DEPENDENT_OBJECT_NAME, DEPENDENT_OBJECT_TYPE,
          BASE_SCHEMA_NAME, BASE_OBJECT_NAME, BASE_OBJECT_TYPE,
          DEPENDENCY_TYPE
   FROM SYS.OBJECT_DEPENDENCIES
   WHERE BASE_SCHEMA_NAME = '<schema>'
     AND BASE_OBJECT_NAME = '<object>'
   ORDER BY DEPENDENT_OBJECT_TYPE, DEPENDENT_OBJECT_NAME
   ```
4. For each discovered dependency (level 1), recursively query for its own dependencies (level 2), then their dependencies (level 3). Stop at depth 3 to avoid runaway query chains.
5. Build the dependency tree. Identify:
   - **Critical shared nodes**: objects that appear in multiple lineage paths (high fan-in)
   - **Dead-end sources**: objects at level N with no further upstream dependencies (likely raw source tables or external feeds)
   - **Cross-schema dependencies**: note any object in a different schema than the starting object
6. Output:
   a. Mermaid flowchart (direction LR):
      ```
      flowchart LR
        SOURCE_TABLE_A --> STAGING_VIEW_B
        SOURCE_TABLE_C --> STAGING_VIEW_B
        STAGING_VIEW_B --> ANALYTICAL_VIEW_D
        ANALYTICAL_VIEW_D --> REPORT_VIEW_E
      ```
   b. Dependency inventory table:
      `LEVEL | OBJECT_NAME | OBJECT_TYPE | SCHEMA | DIRECTION | DEPENDENCY_TYPE`
   c. Summary: N upstream sources, M downstream consumers, K shared nodes, L cross-schema refs.
7. Flag circular dependencies if detected (object A depends on B which depends on A).
8. Recommend `view-explorer` for any VIEW objects found in the lineage.

Guardrails:
- If `SYS.OBJECT_DEPENDENCIES` is inaccessible, advise `CATALOG READ` system privilege and halt gracefully.
- Limit recursion to 3 levels deep. If 3 levels still shows many nodes (> 20), truncate and note the count.
- Cross-schema dependencies are shown with schema prefix. Do not attempt to query schemas the user may not have access to.
- If no dependencies are found in either direction, report clearly — the object may be a standalone table with no views built on it.
- This skill is read-only.
