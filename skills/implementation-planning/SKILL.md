---
name: implementation-planning
description: Turn an approved change request and repository evidence into an ordered, testable implementation plan. Use before implementation; do not activate for unrelated reporting.
---

# Implementation planning

1. Restate observable acceptance criteria and identify missing requirements.
2. Inspect the relevant implementation and tests. Cite concrete files/symbols
   and reuse existing extension points.
3. Break work into small steps with explicit prerequisite relationships.
   Separate independent work from steps that depend on a schema or interface.
4. For each step specify intended behavior, likely files, focused validation,
   and failure/rollback considerations. Keep data migrations and rollout
   compatibility visible.
5. Return a bounded plan, risks, and decisions requiring approval. Do not claim
   tests ran, invent implementation facts, or make code changes in this role.
