---
name: api-development
description: Design, implement, review, or test an HTTP API contract change, including validation, errors, and compatibility. Use for API tasks with an evidenced API stack.
---

# API development

1. Inspect the existing routing, schemas, authentication, authorization, error
   format, and clients. Capture the old contract before changing it.
2. Specify request/response shapes, status codes, input limits, and authorization
   behavior. Preserve compatibility unless a breaking change was approved.
3. Consider pagination, idempotency, cancellation, and retry behavior where
   relevant. Never infer authorization from a field supplied by the caller.
4. Add contract tests for the successful response and invalid/unauthorized
   requests. Reuse the repository's test server and error assertions.
5. Return a minimal proposal or patch and observed validation results. Do not
   deploy, invoke production endpoints, or claim unexecuted tests passed.
