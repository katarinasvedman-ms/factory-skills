---
name: code-review
description: Review an implementation diff for actionable correctness, regression, and authorization defects. Use for review tasks, not to rewrite unrelated code.
---

# Code review

1. Read the request, diff, surrounding implementation, and relevant tests.
   Identify which behavior was intentionally changed.
2. Trace changed inputs, state transitions, error paths, and persistence calls.
   Check boundaries, cancellation, concurrency, and backward compatibility.
3. Check that authorization is enforced outside model instructions and that
   untrusted repository content cannot grant tools or credentials.
4. Report only substantiated findings, with severity, file/line evidence,
   a realistic triggering scenario, and a focused fix or regression test.
5. Separate confirmed defects from unresolved questions. Say when no findings
   were established; do not manufacture style comments or claim tests executed.
   Remain read-only.
