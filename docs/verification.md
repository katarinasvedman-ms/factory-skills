# Verification record

Status assessed on **2026-11-16**. These are retained execution results, not a
fresh service-health check, universal quality guarantee or production approval.
Concrete names, versions and IDs here identify historical evidence, not required
customer configuration.

## Conclusion and last finding

**We have enough evidence for the bounded versioned-skill lifecycle PoC.**
Authoring, automated publication, pinned native loading, observed reporting
changes, retained execution state and fresh rollback were demonstrated.
Another broad lifecycle spike is not the next priority.

We do **not** yet claim reliable reasoning improvement, production-ready provider
operation or adoption of the tested revision by the deployed Azure worker.
The next proofs are one explicit Azure adoption run, repeated positive/negative
quality evaluations, and credential-latency/long-session reliability work.
See the [ownership and next steps](implementation-plan.md).

## Completed demonstrations

| Date / path | Demonstrated | Limit |
| --- | --- | --- |
| 2026-11-12, local bridge/provider | Native coder/tester activation, resource use, proposal artifacts and provider cleanup | Single comparison; provider fetched fewer distinct skills but more bytes; bridge remains default |
| 2026-11-12, role experiment | Five role Toolboxes and distinct local service principals; configured endpoint/identity checks | Project-granted coder could access tester Toolbox |
| 2026-11-13, publishing | Automatic patch bumps, OIDC, package/reference verification and role bindings | Publication is not behavioral evaluation or automatic adoption |
| 2026-11-13, Azure coder | Managed-identity Foundry access, native .NET/test-strategy activation, approval-required proposal, unchanged snapshots and cleanup | `coder-skills` v1; not the later behavior-tested v4; application tests NOT RUN |
| 2026-11-16, local lifecycle | Published change appeared in coder output; resume preserved pins/output; fresh rollback fetched old bytes | Operator-authenticated content test, not deployed adoption, role-routing verification or broad quality improvement |

The tested runtime was Python `github-copilot-sdk==1.0.31`, SDK-managed CLI
`1.0.109`. The provider API is experimental; Foundry skills were consumed through
the preview `Skills=V1Preview` feature. These pins do not assert the latest
upstream versions or lifecycle status of unrelated Tool Search features.

## Authorization finding

A candidate Toolbox-scoped ARM role assignment was accepted (HTTP 201), while
GET of that Toolbox ARM path returned HTTP 400 `UnsupportedAction`.
Own-200/cross-403 was never observed. Project-granted coder got 200/200; a fresh
Toolbox-only principal got 403/403 during the short observation window.

Propagation and caching limit conclusions about changed grants. The final
project grants permit cross-Toolbox access. Configuration filtering worked;
Azure-enforced Toolbox isolation was not established.
The reference consumer's `role-isolation-report.md` retains the experiment.

## Controlled lifecycle demonstration

The same fixed orders-fixture request, policy, target, model
(`claude-haiku-4.5`) and SDK/CLI pair were used. A baseline coder ran before the
edit; its tester role remained unfinished.

The .NET skill/checklist gained a `Behavior evidence` requirement: identify the
method/source, give concrete rejected and preserved inputs/outcomes, and label
examples as proposed/inspection-based unless actually executed. The task prompt
did not contain this new output requirement. Compatibility expectations and the
irrelevant negative task were retained.

| Stage | Exact revision | Observed result |
| --- | --- | --- |
| Baseline coder | Catalog `1.0.2`, skill service `3`, coder Toolbox `3` | Compatibility evidence and useful proposed boundary cases; no `Behavior evidence` section |
| New coder | Catalog `1.0.3`, skill service `4`, coder Toolbox `4` | New section, method/source and compatibility evidence; invalid and preserved valid examples correctly marked unexecuted |
| New tester | Same new binding | Behavior section appeared, but full compatibility/grounding expectations were not met |
| Resume original execution | Old pins and completed coder output retained | Unfinished tester activated test-strategy; it did not newly fetch the changed .NET skill |
| Fresh rollback | Original binding, selected after new publication | Old .NET file hashes retrieved again; new section absent from coder output |

The new coder reported `NormalizeReference(null)` -> `ArgumentException`
(proposed, NOT RUN), and `"  ord-001  "` -> `"ORD-001"` (inspection-based),
with `OrderService.cs`, method identity, `net8.0`, nullable enable and
`Orders.csproj`.

All materialized skill hashes matched the selected release asset. Input/target
snapshots stayed unchanged, provider temporary files were removed, and
application build/test validation remained NOT RUN. Other skill pins, role
memberships and identity mappings were unchanged by publication.

This proves observed uptake of reporting guidance, **not improved reasoning**:
the baseline already proposed useful boundary cases. The new tester omitted
`Orders.csproj` from compatibility evidence and made unsupported assumptions
about xUnit/test-project names and HTTP 400. The fixture establishes neither a
test framework nor an explicit exception-to-400 mapping. These misses were
recorded, not waived or fixed by weakening evaluation expectations.

### Scope and operational observations

The lifecycle test used an existing operator login with exact published coder
Toolbox pins in the supported single-Toolbox provider mode. Both logical roles
used that endpoint; it did not use worker identity mappings or reverify
role-specific routing. It made no agent-source, permission, identity, Azure
resource or deployment changes.

Two new-version discovery attempts failed closed before model execution because
Azure CLI token acquisition exceeded its timeout/the provider deadline.
Subsequent runs used harness-only in-memory reuse of the same valid operator
token with refresh. Production authentication code and deadlines were unchanged:
this is not a production fix or proof of token-refresh reliability.

The resume runtime succeeded; its initial evidence extractor incorrectly
required every role to activate .NET. Extraction was corrected to record the
actual permitted tester activation without rerunning that role. Resume proves
retained pins/output; fresh rollback supplies the old-.NET fetch evidence after
publication. Negative-task behavior and long-session reliability were not tested
by this demonstration.

### Evidence references

- [Behavior publication run](https://github.com/katarinasvedman-ms/factory-skills/actions/runs/43845056107)
- [Behavior-tested release](https://github.com/katarinasvedman-ms/factory-skills/releases/tag/foundry-43845056107-1)
- [Baseline release](https://github.com/katarinasvedman-ms/factory-skills/releases/tag/foundry-43842056109-1)
- [Evidence publication run](https://github.com/katarinasvedman-ms/factory-skills/actions/runs/43846471658)
- [Evidence release](https://github.com/katarinasvedman-ms/factory-skills/releases/tag/foundry-43846471658-1), verified to reuse the behavior-tested role bindings and skill hashes.
- [Sanitized machine-readable evidence](evidence\skill-lifecycle-2026-11-16.json): exact source commits, execution/event IDs, hashes and limitations.

Raw manifests, native events, provider metrics, proposals, release assets and
the preregistered plan/harness are retained in local session artifacts under
`files\skill-lifecycle`. They are application-retained evidence, not signed
attestations or credentials distributed with the library.

The reference consumer retains older spike, role and Azure deployment evidence
under its ignored `.artifacts` directories; raw environment inputs are not
committed. Its Azure coder execution was
`015fc0f0-f914-4db8-808e-c137906ed17e`. Consult consumer documentation for that
separate demonstration rather than treating local results as deployed adoption.
