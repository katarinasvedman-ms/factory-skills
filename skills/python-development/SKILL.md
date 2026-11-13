---
name: python-development
description: Implement, review, or test Python behavior using the repository's interpreter, dependencies, typing, and test conventions. Use only for an evidenced Python stack.
---

# Python development

1. Read interpreter requirements, dependency/lock files, entry points, formatter
   settings, and nearby tests before editing.
2. Preserve public call signatures, exception contracts, encoding, and async
   behavior. Do not block an event loop or swallow cancellation.
3. Use context managers for owned resources, explicit validation at boundaries,
   and existing helpers rather than unnecessary frameworks.
4. Add a focused test demonstrating the regression and its relevant edge case.
   Avoid network-dependent unit tests and implicit global environment changes.
5. Use existing tooling through authorized execution only. Mark unavailable
   checks NOT RUN and distinguish static observations from runtime evidence.
