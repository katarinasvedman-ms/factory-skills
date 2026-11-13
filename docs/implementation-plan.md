# Dynamic Skills Platform: PoC Implementation Plan

## Confirmed implementation choices

The user selected Python with Copilot SDK and both GitHub and Foundry
distribution. The implementation uses SDK 1.0.31 / SDK-managed CLI 1.0.109 and
native file-based consumption for both transports. These choices supersede
the TypeScript/GitHub-first proposals below.

The local skills and factory implementations are now in their corresponding
worktrees. Live SDK consumption and the existing, user-authorized Foundry
project/toolbox path have been exercised. See both repositories' READMEs for
commands, retained evidence, and limitations; no commits/pushes or ACA
deployment have been performed. Container validation is blocked by its package
download TLS/network configuration.

## Starting point and scope

This plan is based on `brief.md` and `skills-factory-handoff.md`.
On 2026-11-12, GitHub reported both supplied repositories as empty. The local
workspace contains the two documents but no factory implementation. There is
therefore no existing language, orchestration, runtime, or infrastructure to
reuse or verify yet.

Use the actual repository names supplied for this initiative:

- `katarinasvedman-ms/ai-factory`: workers, agent definitions, orchestration,
  skills integration, tests, and Azure deployment configuration.
- `katarinasvedman-ms/factory-skills`: portable skills, factory metadata,
  validation, evaluations, and versioned releases.

The brief specifies GitHub-first distribution and five logical roles. The
handoff describes two workers and a possible Toolbox-first experiment, but
explicitly leaves Toolbox unselected. The recommended baseline is GitHub-first,
with a separately gated Toolbox compatibility milestone. Confirm this scope
before implementation; if Toolbox consumption is the primary PoC objective,
move that milestone immediately after the native SDK integration spike.

The first vertical slice uses a simulated change request, an unmodified sample
.NET/SQL Server repository, and coder/tester sessions. Add architect, planner,
and reviewer after proving actual skill consumption. Do not build a complete
ServiceNow integration, enterprise workflow engine, or skill registry.

## Proposed architecture

```text
Simulated change request + target repository/commit
  -> execution coordinator
  -> static repository profiler
  -> catalog selection by role, technology, and task
  -> dependency/compatibility resolution
  -> GitHub SkillResolver at an approved immutable commit
  -> verified execution-local skill directories + persisted manifest
  -> role-specific agent sessions using native skill discovery/loading
  -> patch, review/test evidence, activation events, approval-required result
```

Distribution and consumption remain separate. The resolver retrieves approved
content; the runtime adapter makes it discoverable. Metadata is available at
session startup, while full instructions/resources load when relevant.

**Proposed runtime:** TypeScript with GitHub Copilot SDK for the initial coder
and tester sessions, sharing one worker implementation configured by role.
This minimizes PoC infrastructure; it is not an inferred existing architecture.
If the tester must use a different framework, establish its native loader in
the first milestone instead. Five logical roles do not require five distinct
frameworks or container images.

## Implementation milestones

| Milestone | Work and repository | Exit criterion |
| --- | --- | --- |
| 0. Confirm runtime and scope | In `ai-factory`, record language/framework decisions, exact SDK and underlying CLI versions, model/authentication requirements, and worker topology. Build a minimal native skills-loading experiment. Confirm GitHub-first versus Toolbox-first. | A real SDK session discovers and activates a harmless local skill, reads a supporting resource, and exposes usable evidence of activation. |
| 1. Establish the skills contract | In `factory-skills`, create portable skill folders, catalog schema, validation, ownership rules, and release workflow. Start with `dotnet-development`, `test-strategy`, and `database-changes`, each with resources and positive/negative behavioral fixtures. | CI validates the format, metadata, resources, dependencies, and fixtures; an approved release resolves to exact source content. |
| 2. Implement deterministic resolution | In `ai-factory`, add static profiling, role/task selection, dependency closure, compatibility checks, `SkillResolver`, GitHub retrieval, digest verification, and the execution manifest. | The same request, target commit, policy, and catalog snapshot produce the same role assignments and skill references without executing repository code. |
| 3. Complete the local vertical slice | Materialize separate role-specific skill roots before creating SDK sessions. Run coder then tester against a sample repository using a simulated request. Capture patches, test evidence, skill-load events, and failures. | Appropriate skills actually load and affect observable outputs; irrelevant skills stay inactive; the target repository needs no skill configuration changes. |
| 4. Complete brief coverage | Add architect, planner, and reviewer role configurations and the remaining seven skills: architecture analysis, implementation planning, code review, legacy code analysis, Java, Python, and API development. | All ten skills have useful procedures and focused behavioral tests; all five roles receive appropriate skill sets. |
| 5. Run isolated ACA jobs | Add container configuration and infrastructure-as-code for the agreed worker topology, identities, durable execution artifacts, and logging. Reuse an existing environment only if explicitly supplied and approved. | Fresh and concurrent jobs consume the pinned release independently and persist their manifests/results without sharing mutable execution state. |
| 6. Evaluate Toolbox compatibility | After explicit approval, publish a small approved subset to a Foundry project and pin both toolbox and skill versions. First test discovery/resources and a file-based bridge; evaluate an on-demand provider only if needed. | The same skill behavior and pinning tests pass through the alternative distribution path, with no role-agent changes. Document limitations and a go/no-go decision. |

Milestones 0-3 are the first demonstrable slice. Milestones 4-5 complete the
brief's PoC scope. Milestone 6 is an optional extension, not a prerequisite for
the GitHub baseline.

## Repository deliverables

### `factory-skills`

- `skills\<skill-id>\SKILL.md`, plus references, assets, and scripts only where
  justified. Keep application-specific commands in the application's existing
  instructions, not in generic skills.
- A separate machine-readable catalog: ID, semantic version, relative path,
  applicable roles/technologies, task applicability, prerequisites,
  dependencies, and runtime compatibility.
- Schema/format/resource-link checks, dependency-cycle and duplicate-ID checks,
  focused behavioral fixtures, and a release workflow.
- Versioned releases with a source commit and per-skill content digests.
  Update a skill's semantic version when its content changes. Resolve release
  tags to commits once; never trust a tag alone as an immutable reference.
- Authoring, ownership, approval, release, and rollback documentation.

### `ai-factory`

- A repository profiler that reads manifests/configuration without running
  builds or install scripts; reports evidence, confidence, and unknown stacks.
  Detect multiple stacks and distinguish positive detection from assumptions.
- A deterministic selector based on trusted role/task metadata and profiler
  evidence. Handle unknown stacks with generic skills rather than guesses.
- A narrow `SkillResolver` contract for catalog retrieval and verified package
  materialization. Implement GitHub only initially; keep selection and runtime
  configuration outside the transport implementation.
- GitHub retrieval using narrowly scoped credentials, preferably short-lived
  GitHub App installation tokens for private repositories. Azure managed
  identity does not by itself authorize GitHub repository access.
- Safe extraction, bounded retries/timeouts, digest checks, and execution-local
  staging. Download one pinned snapshot per execution where practical.
  Any cache must be keyed by immutable content and must never fall back to
  unverified or floating content.
- A runtime adapter that supplies selected skill roots through SDK
  `skillDirectories`, with controlled discovery paths and name-collision rules.
  Do not overwrite or implicitly trust target-repository skills.
- A persisted manifest recording execution ID, target repository/commit,
  request/policy/catalog references, roles, skills and assignments, exact
  versions/source commits/digests, and runtime/image/model configuration.
  Persist it before agent work and reuse it on restart. Record actual skill
  activation separately from selection.
- Local run instructions, container/deployment configuration, structured errors
  and logs, integration tests, and a repeatable demonstration.

## Security and failure behavior

Skills are instructions, not authorization. Enforce tool permissions outside
the model, and treat target-repository text as untrusted. Allow only approved
skills and approved dependency closure; reject incompatible, missing,
unauthorized, or tampered required content before starting affected sessions.
Optional omissions must be explicit and recorded, never silently substituted.

Do not execute repository or skill scripts during profiling/bootstrap.
Agent-driven build/test execution requires explicit tool policy and an isolated
worker environment with narrowly scoped credentials, not unrestricted execution
on the developer host. Keep downloaded skills read-only to agents.

For the PoC, produce local patches and approval-required results only; do not
give workers commit, push, or deployment capability. Demonstrate denial of these
actions. Any later approval workflow must authorize an exact action/artifact
through trusted application code, not through prompt text.

## Acceptance and evidence

Use deterministic resolver tests plus separately identified live-runtime
evaluations. Run against fixed application commits and pinned skill snapshots.
Check actual runtime/tool events, resource reads, diffs, and build/test results;
an agent's statement that it used a skill is not evidence.

1. Detect .NET and SQL Server from fixtures and record the evidence; handle
   unknown and mixed-stack fixtures without invented technologies.
2. Select different role-appropriate skill sets, resolve shared dependencies to
   identical versions, and reject cycles/incompatibilities/unauthorized skills.
3. Demonstrate fresh-session discovery, relevant activation, supporting-resource
   access, and non-activation of an available but irrelevant skill.
4. Demonstrate a task-specific observable outcome derived from skill guidance,
   using a controlled with/without-skill comparison where useful.
5. Start execution A, publish release B, and prove that A and its resumed jobs
   retain their original bytes while a newly approved execution can use B.
6. Exercise unavailable GitHub, expired credentials, missing resources, tampered
   packages, unsafe archives, and bounded retry exhaustion. Fail closed without
   silently fetching another version.
7. Run concurrent executions and verify isolation, consistent manifests, and
   retained artifacts after worker exit.
8. Include malicious repository instructions requesting unauthorized skill
   loading or commit/push/deploy actions; verify enforcement independently of
   whether the model follows its skill guidance.

For model-dependent activation cases, record repeat-run outcomes rather than
claiming deterministic behavior. Agree success thresholds during milestone 0.
If the chosen runtime cannot expose skill activation directly, establish an
observable loading mechanism in the spike before claiming that requirement is met.

## Distribution decision

| Option | Recommendation and trade-off |
| --- | --- |
| GitHub pinned source/release | Baseline: fewest new services, independently released skills; requires private-repository authentication and measured startup latency. |
| Foundry Toolbox | Optional managed, Azure-authenticated distribution; adds preview dependencies, resource-discovery integration, and authorization/networking work. |
| OCI in ACR | Consider if artifact signing, replication, or large bundles justify registry packaging; not needed initially. |
| Azure Blob | Consider for simple managed-identity downloads at scale; needs an approved publication/index/version contract. |
| Skills baked into worker images | Useful for a quick smoke test, but not the final path because updates would require image rebuilds. |

## Verified API guidance and remaining decisions

The official SDK documentation currently supports local `skillDirectories`
and describes custom `skillProvider` integration as experimental. Use the
directory-based path first and verify behavior against pinned package/runtime
versions rather than assuming CLI, SDK, and cloud coding agent equivalence.

Foundry documents Toolbox skills as preview MCP Resources discovered through
`resources/list` and retrieved through `resources/read`. Generic MCP tool
support alone does not establish skill consumption. A pinned toolbox must also
contain explicit immutable skill references. Supporting files and script
execution require separate handling.

Before coding, confirm the proposed language/tester runtime, distribution
priority, sample repository and permitted task, Copilot/model access, and
required versus optional skill policy. Azure subscription, region, identities,
and network boundaries are additional gates before any deployment.

References checked on 2026-11-12:

- [Copilot SDK skills](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/skills)
- [Foundry skills and Toolbox discovery](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/skills)

This plan does not authorize provisioning, credential creation, commits,
pushes, or deployment.
