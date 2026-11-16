# Implementation walkthrough: authoring to native skill activation

## Status and verification boundary (2026-11-16)

The PoC demonstrates independent skill publication, Foundry discovery/retrieval,
native Python Copilot SDK activation, local coder/tester sessions, and a live
coder-only Azure Container Apps Job. It is not a complete ticket-to-PR factory.
Workers create approval-required proposals; application builds/tests are NOT RUN.

The tested runtime is `github-copilot-sdk==1.0.31`, SDK-managed CLI `1.0.109`.
The SDK supplies skill loading/activation and the experimental `SkillProvider`
callback interface. Our factory supplies the Foundry adapter, not a replacement
skill engine. Adding a generic MCP server to the SDK is not that adapter.

Two independent version milestones must not be conflated:

| Evidence | Binding used or published | What it proves |
| --- | --- | --- |
| Local bridge/provider comparison, 2026-11-12 | Original `factory-skills` v1 | Both consumption paths, native activation and proposal/resource behavior |
| CI publication, 2026-11-13 | Five role Toolboxes v3 | Automatic versioning, exact package/reference integrity and promoted binding |
| Live Azure coder, 2026-11-13 | `coder-skills` v1 | Managed-identity Foundry access, native activation and proposal generation in ACA |

The Azure execution did not use the latest CI binding. Publishing a release does
not update existing executions or automatically demonstrate its model behavior.
These are retained execution results, not a fresh Azure service-health check.

Paths prefixed `ai-factory` refer to the sibling repository; `factory-skills`
refers to this repository. Historical reports remain useful for exact API
responses, measurements and original test conditions.

## 1. Author a portable skill

Each `factory-skills\skills\<id>\SKILL.md` contains Agent Skills frontmatter
(`name`, `description`) and procedural instructions. Optional references,
scripts and assets live beneath that skill folder and use relative links.
Scripts are content, not permission to execute commands.

`catalog.json` separately holds semantic versions, roles, tasks, technologies,
prerequisites, dependencies and runtime compatibility. `evaluations.json` holds
positive tasks, observable expected outcomes and irrelevant negative tasks.
Validation checks those structures; maintaining expectations is not itself a
successful model evaluation.

Manual edits and direct main pushes are supported for the demo. Copilot can
maintain applicability/evaluation intent when asked for a behavior change.
Mechanical CI versioning does not infer or rewrite that intent.

## 2. Publish from GitHub to Foundry

The implemented path is:

```text
Edit SKILL.md/supporting resources and push main
  -> publish-foundry.yml: version job
       -> compare hashes with the last promoted binding
       -> tools.skills bump_versions: add missing patch increments
       -> bot commits only generated catalog.json changes
  -> reusable ci.yml checks the resulting commit
  -> publish job authenticates with GitHub OIDC
       -> tools.publish_foundry publish_roles
       -> upload changed skill packages; reuse unchanged service pins
       -> create affected role Toolbox versions with exact skill references
       -> verify remote package hashes and Toolbox references
  -> promote a versioned foundry-* GitHub release with role-bindings.json
```

CI preserves explicit higher semantic versions and rejects downgrades.
It publishes from the resulting bot commit, not the original pre-bump SHA.
The bot push does not recursively trigger another workflow. Concurrent/stale
source changes are checked; pushes are never forced.

The verified wording-only .NET change advanced catalog version `1.0.1` to
`1.0.2`, uploaded only that changed skill and created v3 of each affected role
Toolbox. Shared skills use the same service pin in every applicable Toolbox.
Catalog semantic versions, skill service versions and Toolbox versions are
different namespaces.

Evidence:

- [Successful publishing run](https://github.com/katarinasvedman-ms/factory-skills/actions/runs/43410580436)
- [Promoted binding release](https://github.com/katarinasvedman-ms/factory-skills/releases/tag/foundry-43410580436-1)
- [Catalog-only bot commit](https://github.com/katarinasvedman-ms/factory-skills/commit/af553ea430d738ed6e8cdfe9350cef0f009d998b)

This PoC deliberately has no PR/deployment-review click. A Toolbox version is a
versioned composition, not intrinsically an approval record. Production review
policy is separate from pins, hashes and CI checks.

## 3. Adopt the binding and prepare an execution

Download and explicitly select a promoted `role-bindings.json`. Prepare a new
execution with that binding; rollback means preparing a new execution with a
previous binding. The publisher does not change Foundry's floating defaults,
existing manifests, worker credentials or application images.

From `ai-factory`:

```powershell
.\.venv\Scripts\ai-factory.exe prepare --source foundry --skill-mode provider `
  --foundry-binding <downloaded-role-bindings.json> `
  --target .\tests\fixtures\orders `
  --request .\examples\request.json --policy .\examples\provider-policy.json
```

`src\ai_factory\cli.py` constructs a resolver under the shared
`SkillResolver.resolve` interface. Provider mode returns `ProviderSnapshot`
metadata; bridge/local/GitHub return a full `Snapshot`.

`execution.prepare` copies the bounded target snapshot, profiles its static
files and persists `manifest.json` before any model session. The manifest
records roles, assignments, request/policy, source pins, target identity,
runtime versions and integrity information. Provider materialization adds
observed file hashes; native events add activations. Removing the approved
local content mirror does not remove the run manifest.

## 4. Discover and select skills

### Provider mode (opt-in)

`provider.ToolboxProviderResolver` selects each requested role binding.
`ToolboxClient.catalog` verifies the explicit Toolbox/skill versions, initializes
MCP, lists resources and reads `skill://index.json`.

The index contains frontmatter names/descriptions and content references.
The `resources/list` entry description is transport guidance, not necessarily
the skill's selection description. The index avoids reading every SKILL.md.

`ProviderSnapshot.assignments` validates the explicit per-role
`permitted_skills` against discovered pins and allowed skills. The index does
not supply the factory catalog's full role/technology/dependency/compatibility
metadata, so provider mode does not reconstruct it by reading all bodies.
Static target profiling remains worker context.

`ToolboxSkillProvider.list_skills()` returns only the role's permitted names
and descriptions, plus internal per-skill directory pointers required for
relative supporting-file paths. No instruction body is preloaded. The model
selects from the available descriptions; Foundry Tool Search ranking was not
part of the demonstrated path.

### Bridge mode (default)

`resolvers.FoundryResolver` requires a complete approved local skill snapshot.
It discovers the pinned Toolbox, downloads all pinned packages and checks them
against that approved content before selection. `selection.select` applies the
catalog's role/task/technology filters, prerequisites, dependency closure and
runtime compatibility.

Task categories and policy are trusted operator inputs, not authority inferred
from arbitrary repository text. Required availability does not require the
model to activate every available skill.

## 5. Fetch and load an activated skill

The callback ownership is:

```text
SDK requests list_skills()
  -> our adapter discovers/filters Toolbox metadata
  -> SDK exposes permitted skill descriptions to the model

Model activates a skill using the SDK's native skill mechanism
  -> SDK calls our read_skill(name)
  -> our adapter checks permission and retrieves pinned content
  -> SDK loads returned instructions and emits native activation evidence
```

`ToolboxSkillProvider.read_skill` reads
`skill://<name>/SKILL.md`. For an activated multi-file skill it also reads the
advertised MCP archive, validates it and extracts the complete folder into that
session's private temporary directory. Individual supporting files were shown
to be addressable, but this implementation materializes a whole activated
folder, not one file per subsequent read.

`runtime._run` configures the native session with:

```python
skill_provider=provider,
skill_directories=[] if provider else [str(directory / "skills" / role)],
on_permission_request=tools.permission,
available_tools=["skill", *sorted(tools.names)],
enable_skills=True,
mcp_servers={},
```

The empty MCP server configuration is deliberate: our adapter calls Foundry.
The SDK does not independently discover those Toolbox skills through
`mcp_servers`. Bridge mode uses the same native skill engine with verified
local role directories and no provider.

`WorkerTools` exposes bounded snapshot reads, supporting-resource reads and
approval-required proposal artifacts. Tool permissions remain default-deny;
repository instruction/config/plugin discovery is disabled. Tools require an
approved native activation before work. Neither skill content nor bundled
scripts grants a shell, database, commit, push or deployment capability.

## 6. Authentication, role filtering and failure behavior

Both adapters use `DefaultAzureCredential` with scope
`https://ai.azure.com/.default`, observed audience `https://ai.azure.com`, and
the `Foundry-Features: Skills=V1Preview` header. Initial local runs selected
Azure CLI credentials; the role experiment used distinct certificate-backed
service principals; the Azure coder used managed identity for Foundry.
Copilot model authentication is separate.

Five role Toolboxes exist: coder, tester, architect, planner and reviewer.
Our adapter uses the selected endpoint and `permitted_skills`, and checks
expected role identity claims. That is application-enforced filtering,
not an Azure-enforced prohibition on calling another Toolbox.

The role experiment accepted a candidate Toolbox-scoped assignment (HTTP 201),
but the desired own-200/cross-403 access condition was never observed.
Project-granted coder could access both coder and tester endpoints (200/200);
a fresh Toolbox-only principal got 403/403 during the short observation window.
Propagation/caching limits interpretation of changed grants. Treat current
project grants as project-wide access, not proven Toolbox authorization isolation.

Provider reads have bounded retries/backoff and a bounded in-memory cache.
The adapter's 24-second callback budget is below the pinned SDK's 30-second
ceiling. Failed required discovery/activation fails the run; detailed application
errors remain available even when SDK callback exceptions are sanitized.
There is no silent bridge fallback.

`runtime._session` disconnects the SDK before closing the provider and removing
its temporary resources, including tested failure paths. Already materialized
content can be reused locally; new activations/resumed unfinished work may need
Toolbox again. Bridge's prepared full snapshot remains locally usable.

## 7. Evidence: native activation, not agent claims

`runtime._run` handles native `skill.invoked` and `skill.invoked.ref` events,
checks the role's assignment (and provider-loaded state), updates the manifest,
and retains original `notification.to_dict()` records in
`native-skill-events.jsonl`. A successful role result requires an approved native
activation. Provider events report `source: sdk`; file-backed events report
`source: custom`. These are application-retained events, not signed attestations.

| Retained execution | Evidence location in `ai-factory` |
| --- | --- |
| Original bridge `649a473a-9bc3-4176-be92-c7954331b3c9` | `.artifacts\executions\<execution-id>` |
| Provider comparison `79174714-1c23-4d05-83b8-922aacbbec00` | `.artifacts\toolbox-provider-spike\comparison\provider\<execution-id>` |
| Bridge comparison `34125fbd-0730-441d-8675-9d88a964c50c` | `.artifacts\toolbox-provider-spike\comparison\bridge\<execution-id>` |
| Azure coder `015fc0f0-f914-4db8-808e-c137906ed17e` | `.artifacts\coder-deployment\download\executions\<execution-id>` |

The Azure coder run activated `dotnet-development` and `test-strategy`, generated
an `OrderService.cs` proposal, retained unchanged input/target snapshots and
removed provider temporary files. Its separate
`.artifacts\coder-deployment\verification.json` records SDK/CLI pins and two native
activation events. ACR Tasks built the image despite the earlier local Docker
TLS issue; preparation-only and live job executions both succeeded.

Environment-specific deployment inputs and raw evidence are ignored artifacts,
not prerequisites committed with secrets to either public repository.
See `ai-factory\spike-report.md` for exact API shapes, single-sample timings/bytes
and controlled-fault results; see `ai-factory\role-isolation-report.md` for the
scope experiment and limits of its conclusions.

## 8. GitHub versus Foundry and remaining work

| Path | Resolution and SDK handoff | Evidence boundary |
| --- | --- | --- |
| GitHub | Full 40-character approved commit; source ZIP; verified local role directories | Transport/contract tests; no claim here of a live GitHub resolver model session |
| Foundry bridge | Explicit versions; full packages checked against approved local mirror; role directories | Real local coder/tester sessions; default |
| Foundry provider | Explicit role binding; metadata first; activated content only; SDK provider callbacks | Real local coder/tester and Azure coder sessions; experimental opt-in |

Foundry removes the need to build a skill-hosting service, not the need for
runtime integration, explicit policy, release adoption or evidence. The SDK
provider is experimental and the consumed Foundry skills feature is preview.

Remaining work includes an isolated application build/test executor, ticket/
GitHub orchestration and PR return, all-role/concurrent Azure evaluation,
long-session availability/token-refresh/latency testing, evaluation after
adopting newer release bindings, and production least-privilege/review/audit
policy. A passing distribution pipeline proves bytes and references, not model
quality, compilation or production readiness.
