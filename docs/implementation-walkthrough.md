# Implementation walkthrough: discovery to native skill activation

## Conclusion and verification boundary

The retained real execution demonstrates **Foundry Toolbox discovery and
versioned package retrieval, bridged into native Python Copilot SDK skills**.
It does not demonstrate that the SDK natively discovers Toolbox skills through
an MCP server configuration. We use a file-based bridge, not an experimental
`skill_provider`.

This walkthrough was checked against the actual local source and retained
execution artifacts on 2026-11-12. The execution's target/skill integrity was
reverified without making new model calls or deploying anything. The source
files have not been committed/pushed, so references below point to the local
worktrees rather than nonexistent GitHub commit permalinks.

Source paths prefixed with `ai-factory` refer to the sibling repository.
`factory-skills` is this repository. No IKEA-specific registry specification
is present in the supplied documents; the comparison below maps concrete
mechanisms to a registry/discovery pattern, not a claim of exact conformance.

## Actual call sequence

The CLI entry point is `ai-factory\src\ai_factory\cli.py:59-80`.

```text
prepare --source local|github|foundry
  -> construct the chosen resolver
  -> resolver.resolve()                         fetches the complete approved snapshot
  -> Snapshot(...)                             validates content and computes digests
  -> execution.prepare(...)
       -> repository_files(target)
       -> profile(files)
       -> select(snapshot, technologies, roles, tasks, policy)
       -> copy target and selected per-role skill packages
       -> write manifest.json
       -> verify(execution)

run EXECUTION --model MODEL --live
  -> acquire execution lock
  -> verify persisted execution and pin model/runtime configuration
  -> check actual SDK-managed CLI version
  -> create one native SDK session per requested role
  -> observe native skill invocation and controlled resource reads
  -> persist proposal artifacts and role results
```

**Important:** retrieval currently precedes profiling and selection. Foundry
downloads all ten approved packages; only selected packages are materialized
into the role-specific SDK skill directories. Remote retrieval is not lazy.
The progressive disclosure is at the model-context/loading boundary.

## 1. Skill discovery

`ai-factory\src\ai_factory\contracts.py:114` defines `Snapshot`. It reads
`catalog.json`, validates identifiers, semantic versions, role/task/technology
metadata, frontmatter, resources, and dependency graphs, and creates per-file
and per-skill SHA-256 records.

The factory metadata source is `factory-skills\catalog.json`. It is separate
from portable `SKILL.md` content. For example, `dotnet-development` declares
version `1.0.1`, .NET applicability, five eligible roles, a .NET prerequisite,
and Python Copilot SDK compatibility.

Foundry adds real service discovery in
`ai-factory\src\ai_factory\resolvers.py:192-257`:

```python
page = self.rpc("resources/list", {"cursor": cursor} if cursor else {})
# ...collect advertised resources and handle pagination...
uri = f"skill://{name}/SKILL.md"
resource = self.rpc("resources/read", {"uri": uri})
```

The advertised resources must include every approved binding entry. Their
instruction text must match the approved local content. Role/technology/task
metadata still comes from our catalog, not from Toolbox resource descriptions.
This is allowlisted discovery, not unrestricted exploration of the project.

## 2. Skill selection

`ai-factory\src\ai_factory\profile.py:28,51` reads the prepared application
checkout without executing it. Project manifests and configuration provide
evidence for .NET, Java, Python, API, and SQL Server characteristics.

`ai-factory\src\ai_factory\execution.py:73` passes that evidence, explicit
roles/task categories, and trusted policy to `selection.select`.

The actual predicate in `ai-factory\src\ai_factory\selection.py:42-49` is:

```python
if (
    name in approved
    and role in entry["roles"]
    and ("*" in entry["technologies"] or tech.intersection(entry["technologies"]))
    and ("*" in entry["tasks"] or set(tasks).intersection(entry["tasks"]))
):
    include(name)
```

`include` also enforces runtime compatibility, prerequisites, dependency
closure, and role authorization for dependencies. Explicit required skills
must pass those checks too. Unknown/missing/unauthorized requirements fail
closed.

Task categories are operator/platform input, not inferred from arbitrary
repository prose. `required_skills` means required **availability**, not a
requirement for the model to activate every listed skill.

In the retained Foundry run, the profiler detected `api`, `dotnet`, and
`sqlserver`. The trusted tasks were `implementation` and `testing`, so both
coder and tester received `dotnet-development` and `test-strategy`, not the
API/database skills. Their eventual activations differed. This particular live
run does not demonstrate different available packages per role.

## 3. Manifest creation and execution consistency

`ai-factory\src\ai_factory\execution.py:53-122` generates a UUID, copies the
target snapshot and selected role packages, then persists `manifest.json`
before any model session starts:

```python
"assignments": assignments,
"distribution": snapshot.source,
"catalog_sha256": snapshot.catalog_sha256,
"skills": {name: snapshot.records[name] for name in selected},
```

The manifest also contains target commit/dirty state when available, target
file hashes, profiling evidence, policy/request hashes, and SDK/CLI versions.
This fixture has no Git commit: its manifest explicitly records `commit: null`
and identifies the target by its content digest.

Semantic skill versions and Foundry service versions are distinct:

| Skill | Catalog version | Foundry immutable version |
| --- | --- | --- |
| `dotnet-development` | `1.0.1` | `1` |
| `test-strategy` | `1.0.0` | `1` |

`execution.verify` at line 125 checks the retained target and role package
bytes against the manifest. Resume uses those persisted packages, not current
upstream defaults. `runtime.json` separately fixes model/runtime configuration
when the execution is first run.

## 4. GitHub versus Toolbox retrieval

Both implement the narrow `SkillResolver.resolve() -> Snapshot` contract in
`ai-factory\src\ai_factory\resolvers.py:17`.

| Detail | GitHub resolver, line 72 | Foundry resolver, line 126 |
| --- | --- | --- |
| Approved source | Repository plus full 40-character commit SHA | Approved local skills snapshot plus project/toolbox/skill version binding |
| Authentication | Scoped token or local `gh` authentication | `DefaultAzureCredential`, scope `https://ai.azure.com/.default` |
| Retrieval | GitHub source ZIP at the pinned commit | Pinned toolbox metadata, MCP resources, then pinned Skills API ZIPs |
| Integrity basis | Authenticated immutable commit content; computed file/package digests | Exact comparison of discovered instructions and downloaded package bytes with approved local content |
| SDK handoff | Verified local role directories | The same verified local role directories |
| Live verification | Not yet exercised against the initially empty skills repository | Exercised against the supplied existing Foundry project |

GitHub calls `/repos/{repository}/zipball/{commit}`. Its restricted codeload
redirect does not receive the GitHub authorization header.

Foundry first checks:

```text
GET {project}/toolboxes/{name}/versions/{version}?api-version=v1
```

It rejects missing/floating/mismatched expected skill references, initializes
MCP at the version-specific toolbox endpoint, and uses `resources/list` and
`resources/read`. It then obtains every full package through:

```text
GET {project}/skills/{name}/versions/{version}/content?api-version=v1
```

Full ZIP retrieval preserves supporting resources. Packages are safely unpacked
and must match the approved bytes before a `Snapshot` is returned.

The producer is `factory-skills\tools\publish_foundry.py:13-51`. It uploads
each skill folder as a ZIP and creates a toolbox version containing explicit
`skill_reference` versions. Its generated binding is retained in
`factory-skills\.artifacts\foundry-binding.json`.

## 5. Native Copilot SDK loading

`ai-factory\src\ai_factory\runtime.py:290-335` creates actual Python SDK
sessions. Relevant arguments, copied from the implementation:

```python
tools=tools.definitions(),
available_tools=["skill", *sorted(tools.names)],
on_permission_request=tools.permission,
skill_directories=[str(directory / "skills" / role)],
enable_skills=True,
included_builtin_skills=[],
enable_config_discovery=False,
skip_custom_instructions=True,
enable_file_hooks=False,
enable_host_git_operations=False,
mcp_servers={},
on_event=on_event,
```

`mcp_servers={}` is deliberate: the SDK consumes verified local skills after
the bridge completes. It does not connect directly to Toolbox.

The role prompt contains generic workflow/tool guidance, not the ten skills'
full instructions. Native `skill` invocation loads relevant instructions;
`WorkerTools.read_resource` at line 50 supplies approved supporting files on
demand with a digest check.

The prompt asks for at least one relevant skill before work, and worker tools
reject calls until an approved native invocation has been observed. Therefore
this is configured, enforced participation in the skills workflow, not evidence
that an otherwise unconfigured SDK always activates skills spontaneously.

## 6. Evidence of actual activation

`ai-factory\src\ai_factory\runtime.py:280-288` translates native SDK events,
not assistant prose, into retained activation records:

```python
kind = getattr(notification.type, "value", str(notification.type))
if kind in {"skill.invoked", "skill.invoked.ref"}:
    name = notification.data.name
    if name not in manifest["assignments"][role]:
        violations.append(name)
    else:
        activated.append(name)
    event(directory, "skill.activated", role=role, skill=name)
```

An unapproved invocation causes execution failure. A role result is not accepted
if no native activation was observed.

The retained Foundry execution is:

```text
ai-factory\.artifacts\executions\649a473a-9bc3-4176-be92-c7954331b3c9
```

Its manifest records the supplied project, toolbox `factory-skills`, toolbox
version `1`, all ten immutable service skill references at version `1`, SDK
`1.0.31`, and SDK-managed CLI `1.0.109`. Both sessions used
`claude-haiku-4.5`.

Selected actual `events.jsonl` records, times in UTC:

| Time on 2026-11-12 | Event | Role | Skill/resource |
| --- | --- | --- | --- |
| 15:16:11.377615 | `skill.activated` | coder | `dotnet-development` |
| 15:16:16.055903 | `skill.resource_read` | coder | `dotnet-development`, `references/validation.md` |
| 15:16:21.426909 | `proposal.created` | coder | `OrderService.cs` |
| 15:16:32.587588 | `skill.activated` | tester | `test-strategy` |
| 15:16:32.693987 | `skill.activated` | tester | `dotnet-development` |
| 15:16:32.711791 | `proposals.read` | tester | coder proposal |
| 15:16:35.917996 | `skill.resource_read` | tester | `dotnet-development`, `references/validation.md` |

The proposal adds a whitespace/null guard and `ArgumentException`, preserving
`Trim().ToUpperInvariant()` for valid input. The coder's final artifact contains
the compatibility evidence requested by the skill. The target snapshot remains
unchanged. This is observable proposal/resource behavior, **not proof that the
generated C# compiles or its application tests pass**; both role artifacts mark
application validation NOT RUN.

These are application-retained, transformed SDK events, not signed/raw event
attestations. No raw HTTP request/response capture was retained for independent
network replay. The evidence supports the successful historical code path,
not a fresh service health check or tamper-proof production audit.

The separate opt-in check in
`ai-factory\tests\test_live_demo.py:16` uses local distribution with real SDK
sessions. It asserts native events, resource reads, compatibility details,
proposal creation, unchanged target bytes, and non-activation of available but
irrelevant API/database skills. It is not itself a live Foundry transport test.

To reverify the saved execution without another model call, from `ai-factory`:

```powershell
.\.venv\Scripts\ai-factory.exe verify `
  .artifacts\executions\649a473a-9bc3-4176-be92-c7954331b3c9
```

## Registry/discovery assessment

| Pattern responsibility | Actual implementation | Remaining qualification |
| --- | --- | --- |
| Central authoring/registration | Skills repository and versioned Foundry publication | No separate custom registry server |
| Discoverable catalog | Factory catalog plus Toolbox MCP Resources | Role/task metadata remains local catalog metadata |
| Contextual selection | Profiler, deterministic policy filters, dependency checks | Selection happens after full retrieval |
| Immutable resolution | Git commit or explicit Toolbox/skill versions; execution manifest | Foundry currently needs a full approved local mirror to compare bytes |
| Runtime activation | Native SDK skill loader and invocation events | File bridge required; no demonstrated native SDK Toolbox integration |
| Authorization and audit | Scoped identities, constrained tools, digests and execution events | No toolbox-level RBAC isolation claim; no tamper-evident audit store |

**Architecture implication:** Foundry is a credible managed distribution
option for this PoC; the actual working bridge removes the need to build a
skill-hosting service. It does not remove the need for factory-specific
selection, trusted approval metadata, integrity checks, manifest creation,
and a client adapter.

Before calling this an independently hosted registry/discovery solution, replace
the full local mirror requirement with a trusted release descriptor/catalog
and approved digests, and separate metadata discovery from fetching selected
packages. Those are follow-on changes, not capabilities already implemented.

Deployment readiness is separate: the Docker build is still blocked by package
download TLS failures; ACA identity/network/persistence behavior is unverified;
the tester has no application command runner; GitHub live retrieval awaits an
approved published commit. No deployment or implementation changes were made
as part of this walkthrough.
