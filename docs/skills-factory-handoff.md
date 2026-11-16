# Skills producer and consumer handoff

## Responsibility split

| Producer: skills library | Consumer: agents/runtime |
| --- | --- |
| Portable instructions and supporting resources | Repository inspection and task context |
| Applicability metadata and evaluation expectations | Role selection, allow-lists and dependency handling |
| Source validation, package integrity and publication | Native loading/activation and execution evidence |
| Immutable release binding | Explicit release adoption and pinned run manifest |
| Content-quality improvements | Tool authorization, credentials, deployment and operational reliability |

Do not edit the other session's worktree or expand its permissions as a side
effect of ordinary skill authoring. A new skill's publication is not permission
for every role to use it.

## Release contract

Supply a promoted versioned release containing `role-bindings.json`. It records
exact Toolbox/skill pins, role identity mappings, source provenance and content
hashes. The producer reuses unchanged skill versions and verifies remote bytes
and exact Toolbox composition before promotion.

The consumer selects a binding for a new execution and validates its own
identity/role configuration. Existing runs retain their pins. Rollback selects a
previous binding for a new run; it does not rewrite an old manifest or delete
service versions. Catalog semantic, skill service and Toolbox versions are
different namespaces.

## Runtime adapter contract

The SDK supplies native skill discovery/loading and activation callbacks.
The adapter connects those operations to the registry:

| Operation | Adapter responsibility |
| --- | --- |
| List available skills | Read pinned discovery metadata and expose only permitted descriptors |
| Read activated skill | Validate eligibility and fetch exact instructions |
| Resolve supporting paths | Materialize the activated folder safely and supply its base directory |
| Close session | Remove temporary resources, retaining appropriate execution evidence |

Registry authentication, token refresh, bounded retries/cache and fail-closed
behavior remain application responsibilities. Skills are MCP resources, not
ordinary tool calls. Do not assume generic MCP tool support loads instructions.

A different runtime needs an equivalent integration; the proven SDK adapter
does not prove a universal registry client or agent execution engine.

## Security and evidence

Keep published availability, application allow-lists and Azure authorization
distinct. Separate Toolboxes and identities do not by themselves establish
per-Toolbox access isolation. Skills describe procedures; tools and credentials
determine capabilities.

Require native activation events, supporting-resource reads, observed content
hashes and concrete grounded outcomes when claiming behavioral verification.
Evaluation expectations or agent self-reports are not substitutes.

The [verification record](verification.md) contains completed proof and misses.
The [remaining-work plan](implementation-plan.md) assigns the next narrow checks.
Do not reopen the completed lifecycle proof merely because production readiness
remains unproven.
