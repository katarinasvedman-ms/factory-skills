---
name: legacy-code-analysis
description: Recover behavior and safe change seams in legacy or poorly documented code. Use for legacy modernization and characterization, not ordinary new code.
---

# Legacy code analysis

1. Trace one requested behavior using callers, data access, configuration, and
   error handling. Prefer evidence over naming or historical assumptions.
2. Identify observable contracts, hidden side effects, shared state, and
   consumers that may depend on quirks.
3. Propose characterization tests around current behavior before refactoring.
   Explicitly distinguish preserved quirks from approved behavior changes.
4. Find the smallest seam for the change. Avoid wholesale rewrites or dependency
   upgrades unless required by the request.
5. Return a behavior map with source references, uncertain areas, a minimal
   change proposal, and a rollback/verification strategy.
