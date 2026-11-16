# Remaining work and proof boundaries

## Decision

**The bounded skills-lifecycle PoC is sufficiently demonstrated.** Do not expand
it into another broad registry or framework spike before addressing the focused
gaps below. Recorded evidence supports authoring, CI publication, pinned native
activation, observed reporting-guidance uptake, preserved execution state and
fresh rollback.

It does not establish reliable reasoning improvement, an autonomous factory
or production-ready runtime operations. See [verification](verification.md).
The original exploratory plan is retained in Git history; this is the current
handoff, not a claim that every original acceptance criterion has passed.

## Next proofs

| Question | Bounded next step | Acceptance evidence | Owner |
| --- | --- | --- | --- |
| Has a deployed worker adopted the tested release? | Explicitly select the behavior-tested binding for one new Azure execution | Manifest pins, materialized hashes, native activation and concrete output match the selected release; old executions remain unchanged | Consumer/runtime |
| Do skills reliably help without inventing context? | Repeat fixed relevant and irrelevant tasks; compare with/without skill guidance under a declared rubric | Activation/non-activation counts and grounded outcomes; report misses, not just averages or successful samples | Skills and consumer |
| Is provider operation reliable? | Investigate credential acquisition latency; exercise refresh, interruptions, longer sessions and unavailable required content | Bounded failure, no accepted success after required activation failure, cleanup, and measured latency | Consumer/runtime |

Do not treat the lifecycle harness's local token reuse as a production fix.
Do not weaken evaluation expectations to accommodate grounding or compliance
misses. Keep the provider opt-in and the bridge as an explicit fallback until
the operational adoption decision is supported.

## Ownership boundary

The skills session may improve portable guidance and evaluation expectations,
validate/publish the library and supply an exact release binding.
The consumer session owns agent code, selection experiments, worker credentials,
deployment configuration and native execution evidence.

A separate isolated application build/test executor and ticket/PR integration
are broader factory work, not prerequisites to demonstrating skill publication.
They remain necessary before claiming verified generated application behavior
or complete delivery.

## Constraints

- Keep tool permissions, role allow-lists and credential boundaries explicit.
- No skill-authoring change implicitly authorizes resources or deployment.
- Do not equate project grants or configured role endpoints with Toolbox-level
  authorization isolation.
- Pin each execution. New publication must not silently update an active run.
- Report SDK experimental/Foundry preview dependencies and actual tested pins.
- Keep environment inputs and credentials out of portable skills and source.

Concrete historical version numbers, execution IDs and failed/successful
observations belong in the dated [verification record](verification.md), not
reusable setup instructions.
