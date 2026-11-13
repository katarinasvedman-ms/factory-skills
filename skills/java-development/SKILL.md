---
name: java-development
description: Implement, review, or test Java changes using existing Maven or Gradle configuration and Java release constraints. Use only when repository evidence establishes Java.
---

# Java development

1. Inspect Maven/Gradle configuration, toolchains, dependency versions, package
   structure, and test framework. Do not upgrade Java or the build system.
2. Preserve public API contracts, checked exception behavior, resource ownership,
   transaction boundaries, and existing nullability conventions.
3. Reuse established dependency injection, logging, and serialization patterns.
   Do not expose secrets or introduce unbounded retries/shared mutable state.
4. Add focused regression cases for the changed behavior and boundary failures.
   Identify the smallest existing build/test target.
5. Execute only with authorized tools. Report commands and observed outcomes,
   or mark them NOT RUN. Return source-grounded findings or a minimal patch.
