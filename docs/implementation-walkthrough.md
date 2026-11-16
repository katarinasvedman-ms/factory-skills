# Authoring to native skill activation

This walkthrough describes the reusable lifecycle and the reference consumer's
actual implementation paths. Customer names, resource IDs, machine paths and
historical execution transcripts are not setup requirements.
See [verification](verification.md) for dated evidence and limitations.

## 1. Components and ownership

```text
Portable skill + applicability catalog + evaluation expectations
  -> CI validation/versioning
  -> immutable registry publication and release binding
  -> consumer selects binding and creates run manifest
  -> native runtime requests eligible skill metadata
  -> model activates a skill
  -> adapter retrieves pinned content
  -> native runtime loads instructions
  -> authorized tools produce artifacts and activation evidence
```

This library owns authoring/publication. The reference consumer in `ai-factory`
owns orchestration, policy, execution manifests and its Foundry adapter.
The SDK owns native selection/activation/loading; we did not replace its skill
engine. A registry, adapter and explicit policy may be reusable, but another
runtime needs its own integration and verification.

## 2. Author the skill and its expectations

Use `skills\<id>\SKILL.md` with `name` and `description` frontmatter.
Supporting resources live below the skill directory and use relative links.
The description should distinguish relevant tasks from irrelevant tasks without
embedding customer configuration or granting capabilities.

Keep factory metadata in `catalog.json`: version, roles, tasks, technologies,
prerequisites, dependencies and compatibility. Maintain a realistic positive
task, observable expectations and an irrelevant negative task in
`evaluations.json`. Skill validation checks these records, not model success.

Preserve applicability unless the requested behavior changes it. Shared
procedures remain portable; application commands and project settings are
evidence the consumer must inspect, not assumptions baked into a shared skill.

## 3. Publish through CI

`.github\workflows\publish-foundry.yml` implements:

```text
main push or main dispatch
  -> compare file hashes with the last promoted binding
  -> tools.skills bump_versions
       -> add missing patch increments, preserve higher versions
       -> reject downgrades
  -> commit only generated catalog changes when needed
  -> reusable ci.yml checks that resulting commit
  -> OIDC authentication
  -> tools.publish_foundry publish_roles
       -> publish changed packages; reuse unchanged pins
       -> create affected role Toolbox versions
       -> verify remote package hashes and exact references
  -> promote a foundry-* release containing role-bindings.json
```

Role/task/technology metadata and evaluation intent are not inferred by CI.
The bot push does not trigger a recursive workflow. Stale-source checks,
serialization and non-forced pushes protect the source/version relationship.
Failures can leave unused immutable versions but do not promote an unverified
binding. Never delete older versions or bypass checks to retry.

A version records composition/provenance, not necessarily human review.
The demo has no PR/deployment-review click; production governance is a separate
policy decision. Publication verifies content and references, not model quality.

## 4. Adopt the release and persist an execution

The consumer explicitly selects a promoted binding. Publication does not change
running jobs, existing manifests, worker credentials or service defaults.
Rollback means a new execution using an earlier binding.

Reference consumer paths:

| Concern | Implementation |
| --- | --- |
| CLI source/mode selection | `src\ai_factory\cli.py` |
| Resolver contract and full snapshots | `src\ai_factory\resolvers.py` |
| Provider discovery and callbacks | `src\ai_factory\provider.py` |
| Static target profiling and catalog selection | `src\ai_factory\profile.py`, `selection.py` |
| Manifest creation/integrity | `src\ai_factory\execution.py` |
| Native sessions, permissions and events | `src\ai_factory\runtime.py` |

`execution.prepare` copies a bounded target snapshot, records static evidence and
persists pins, request/policy, role assignments, target identity and runtime
versions before model work. Provider materialization adds observed hashes;
native activation adds event records. No approved local mirror does not mean
no execution manifest.

## 5. Discover, select and retrieve

The SDK's experimental `SkillProvider` interface has `list_skills()` and
`read_skill(name)` callbacks. Our `ToolboxSkillProvider` implements them against
Foundry. The SDK knows when to request a skill; the adapter knows where and how
to fetch it.

### Provider mode (opt-in)

`ToolboxProviderResolver` selects pinned bindings.
`ToolboxClient.catalog` verifies version metadata, initializes MCP, lists
resources and reads `skill://index.json`. Its frontmatter names/descriptions
support selection without reading unactivated instruction bodies. A
`resources/list` entry description may instead be transport guidance.

`ProviderSnapshot.assignments` validates explicit `permitted_skills` against
discovered pins and allowed skills. The index lacks the reference consumer's
full role/technology/dependency/compatibility metadata; provider mode does not
invent it from all instruction bodies.

`list_skills()` exposes eligible names/descriptions plus internal directory
pointers needed for supporting paths. The model chooses from that catalog.
Foundry Tool Search ranking is not part of this verified path.

`read_skill(name)` checks eligibility and reads
`skill://<name>/SKILL.md`. For multi-file skills it fetches the advertised archive,
validates it and materializes the complete activated folder in a private session
directory. This is lazy per skill, not one supporting-file fetch per later read.

### Bridge mode (default)

`FoundryResolver` requires a complete approved local snapshot, fetches the
pinned packages and compares them with approved bytes. Catalog selection then
applies role/task/technology filters, prerequisites, dependencies and
compatibility. Selected role directories go to the native SDK loader.

The GitHub resolver similarly hands off verified directories, but resolves source
at an approved full commit SHA. A floating tag or `main` is not that pin.

### Native session handoff

The reference runtime supplies:

```python
skill_provider=provider,
skill_directories=[] if provider else [str(directory / "skills" / role)],
on_permission_request=tools.permission,
available_tools=["skill", *sorted(tools.names)],
enable_skills=True,
mcp_servers={},
```

Our adapter calls Foundry; the empty MCP configuration is intentional.
Generic MCP connectivity is not a built-in SDK Foundry skill connector.
Approved availability also does not require the model to activate every skill.

## 6. Authenticate and enforce the right boundary

Both Foundry adapters use `DefaultAzureCredential`, scope
`https://ai.azure.com/.default` and `Foundry-Features: Skills=V1Preview`.
The observed audience is `https://ai.azure.com`. Credential refresh and
appropriate identity selection are consumer responsibilities. Registry, model
and publisher credentials are distinct.

The role-aware provider selects the configured endpoint, checks expected
identity claims and filters skills using `permitted_skills`. These checks are
application enforcement. The executed scope experiment did not establish
Toolbox-level authorization isolation; project grants allowed cross-Toolbox
access. Do not describe a separate endpoint as an authorization boundary.

Repository text is untrusted context. Default-deny tools and bounded paths are
enforced outside the model. Skills and bundled scripts do not grant shell,
database, commit, push or deployment access.

## 7. Fail and clean up explicitly

Provider reads have bounded retries/backoff and a bounded in-memory cache.
The tested adapter has a 24-second callback budget below the pinned SDK's
30-second ceiling. Required discovery/activation failure fails the run; detailed
application errors remain available even if SDK callback exceptions are
sanitized. No automatic bridge fallback is performed.

The runtime disconnects the session before removing provider temporary files,
including tested failure paths. Metadata, manifests, hashes and evidence remain.
Already materialized content may be reusable; unfinished resumed work or a new
activation can require registry availability again. Bridge snapshots remain
local after preparation.

## 8. Distinguish the proof levels

| Evidence | What it establishes | What it does not establish |
| --- | --- | --- |
| Schema/unit/distribution checks | Structure, reproducibility, bytes and references | Native activation or useful model behavior |
| Native activation and resource-read events | Actual loading and supporting-file use | Correct conclusions or task completion |
| Grounded output matching changed guidance | Observed uptake in that scenario | General improvement or reliable all-role compliance |
| Retained pins/hashes and fresh rollback | Reproducible content selection | Identical stochastic model output |
| Deployed execution using a binding | Adoption by that worker | Adoption by every role or production readiness |

The reference runtime checks native `skill.invoked` / `skill.invoked.ref` events,
role assignments and provider-loaded state. A successful role result requires
an approved activation. Original SDK event records are retained; they are not
signed attestations. Provider events use `source: sdk`; file-backed events use
`source: custom`.

The bounded lifecycle proof is sufficient for its PoC claim. Further work should
target deployed adoption, grounded repeated evaluations and operational
reliability, as described in the [remaining-work plan](implementation-plan.md).

## 9. Controlled skill lifecycle demonstration (2026-11-16)

The dated demonstration, exact release links, execution/event IDs, content/result
hashes and known misses are retained in the [verification record](verification.md)
and [machine-readable evidence](evidence\skill-lifecycle-2026-11-16.json).
Historical specifics are evidence, not requirements for reusing the pattern.
