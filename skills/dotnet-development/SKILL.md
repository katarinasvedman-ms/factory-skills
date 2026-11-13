---
name: dotnet-development
description: Implement, inspect, review, or test C# and .NET changes using the repository's target framework and conventions. Use when project files establish .NET, not for Java or Python tasks.
---

# .NET development

1. Read project files, SDK pins, analyzers, nullable settings, dependency
   registration, and nearby tests. Do not upgrade the target framework.
2. Trace the relevant C# call path. Preserve public contracts, async behavior,
   cancellation propagation, and dependency lifetimes.
3. Prefer existing abstractions and validation/error conventions. Avoid
   blocking async calls, undisposed resources, and leaking internal exceptions.
4. Read [the validation checklist](references/validation.md) before returning
   a .NET implementation proposal or review.
5. Add focused behavioral regression tests using the existing test framework.
   Run build/test commands only through approved execution tools.
6. When execution is not permitted, return a patch/proposal and mark validation
   NOT RUN. Never imply that source inspection proves a build succeeds.

Before submitting your final response, include the compatibility evidence
required by the validation checklist. Reading the checklist is not sufficient:
the observed project settings must appear in the final response.
