---
name: test-strategy
description: Design focused regression tests and an evidence-based verification plan for a software change. Use when implementing or testing behavior, not for prose-only tasks.
---

# Test strategy

1. Read the acceptance criteria and existing tests before choosing a runner.
2. Build a behavior matrix: normal case, boundary, invalid input, and relevant
   failure/retry cases. Prioritize externally observable regressions.
3. Propose a small test that fails before the fix and passes afterward.
   Use established fixtures and assertions; avoid tests that restate constants.
4. Separate deterministic unit checks from integration tests and live model
   evaluations. Identify credentials, tools, services, and isolation required.
5. Execute only through explicitly authorized tools. If execution is unavailable,
   return proposed tests and exact validation steps marked NOT RUN.
6. Report observed results, limitations, and uncovered risk. Never substitute
   the agent's confidence or self-reported skill use for runtime evidence.
