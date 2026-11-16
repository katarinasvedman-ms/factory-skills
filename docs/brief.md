# Scope: portable skills for role-based agents

## Goal

Maintain reusable engineering guidance independently of agent code and target
application repositories. A consumer should discover relevant instructions,
resolve exact versions and activate them through its runtime without embedding
every skill in an image or prompt.

This is a skills library and release lifecycle, not an orchestration framework,
an authorization service or a promise of autonomous application delivery.
See the [verification record](verification.md) for what has actually been shown.

## Ownership

The library owns portable content, applicability metadata, evaluation
expectations and versioned publication. Consumers own repository inspection,
role/task selection, execution manifests, runtime adapters and tool permissions.
The [handoff](skills-factory-handoff.md) defines that boundary.

## Content contract

- One directory per skill, containing Agent Skills `SKILL.md` frontmatter and
  actionable instructions, with optional relative supporting resources.
- A separate catalog for semantic versions, roles, tasks, technologies,
  prerequisites, dependencies and compatibility.
- Positive and irrelevant negative evaluation tasks with observable outcomes.
- Application-specific commands and configuration remain application context.
- Scripts are supporting content; their presence does not authorize execution.

The current library covers architecture analysis, implementation planning, code
review, test strategy, legacy analysis, .NET, Java, Python, API development and
SQL Server database changes. Technology-specific skills remain deliberately
specific; "generic" means customer-independent, not erasing applicability.

## Distribution and consumption

Distribution supplies pinned content. Consumption makes it available through
the runtime's native discovery/loading mechanism. A generic MCP connection alone
does not establish skill activation.

The implemented paths are GitHub commit-pinned source and Foundry Toolbox.
The reference consumer supports a verified file bridge and an experimental
on-demand provider. Neither requires inventing a custom skill engine.
No OCI/Blob distribution path is implemented.

The reusable-pattern hypothesis is:

```text
Versioned instruction registry
  -> runtime-native adapter
  -> explicit execution policy and version manifest
  -> observable activation and grounded outcomes
```

The Copilot SDK integration demonstrates one instance, not universal support
across runtimes. A different runtime still needs its own loading, permission,
credential and evidence integration.

## Required invariants

Pin source and skill versions per execution. Shared skills use the same pin
where applicable; a new release must not silently change existing runs.
Distinguish availability from activation, and activation from correct output.

Reject unavailable, unauthorized or tampered required content. Treat repository
text as untrusted input. Enforce capabilities outside the model; skills cannot
grant tools or bypass authorization. Separate role Toolboxes organize exposure
but are not a proven authorization boundary.

## Acceptance boundary

The bounded lifecycle PoC has sufficient evidence for publishing, observed
guidance uptake, pin preservation and rollback. Production readiness, reliable
quality improvement and deployed adoption of each new release require separate
proof. The [remaining work](implementation-plan.md) is deliberately focused.

Earlier exploratory requirements are retained in Git history, not repeated here
as claims of completed factory capabilities.
