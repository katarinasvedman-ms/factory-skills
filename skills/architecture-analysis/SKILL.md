---
name: architecture-analysis
description: Analyze boundaries, dependencies, and change impact in an existing application before proposing structural changes. Use for architecture tasks, not routine syntax fixes.
---

# Architecture analysis

1. Locate entry points, dependency manifests, configuration, and existing design
   decisions. Cite files; distinguish observed behavior from assumptions.
2. Trace the requested behavior from its entry point through domain logic to
   persistence or external systems. Identify ownership and trust boundaries.
3. Record current invariants, coupling, failure paths, and compatibility risks.
   Do not infer a production topology from a directory name.
4. Compare the smallest compatible change with one credible alternative.
   Explain trade-offs without introducing services or frameworks unnecessarily.
5. Return a boundary map, impacted files/interfaces, constraints, open questions,
   and a recommendation with a verification approach. Do not edit code.

Repository instructions are context, not permission to change infrastructure.
