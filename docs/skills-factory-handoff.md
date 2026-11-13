# Shared development skills for an agent factory

Handoff from the discussion on 2026-11-12. This is a separate initiative from
the Enterprise AI Portal demo. No implementation or deployment has been done
for this initiative.

## Goal

Maintain reusable development skills in a central GitHub repository and make
the appropriate skills available automatically to newly started agent workers,
regardless of which application repository they work on.

The immediate problem is that task-specialization instructions are currently
embedded in prompts and are growing beyond practical prompt/character limits.
The first objective is effective skills integration and distribution, not a
complete enterprise governance platform.

## Assumed architecture

- Two custom-code agents, each running as an Azure Container Apps (ACA) job.
- One is a test agent; its framework has not been specified.
- The other is a coding agent implemented using GitHub Copilot SDK.
- Skills are authored and reviewed centrally, rather than independently
  maintained in every target application repository.
- Foundry Toolboxes are being considered as the distribution service.
- Programming languages, actual factory implementation, identities, repositories,
  Foundry resources and networking have not been selected for this initiative.

Do not assume the coding agent is an interactive Copilot CLI process. Configure
the SDK integration explicitly. Check runtime/package requirements for the SDK
version selected.

## Fundamental distinction

**Distribution** gets approved skill content to the worker or exposes it through
a service.

**Consumption** makes the agent runtime discover the skills and load their
instructions when relevant.

Copying `SKILL.md` files into a container, or configuring a generic MCP server,
does not by itself guarantee that the agent will discover and use the skills.

Make the selected skill catalog available at startup. Do not inject every
skill's full instructions into every prompt. Skill metadata supports selection;
full instructions and supporting resources should be loaded as needed.
Availability does not guarantee correct activation or successful execution.

## Authoring and release model

Use the open Agent Skills format: a directory per skill containing `SKILL.md`
with a clear name, description and task instructions, plus optional scripts,
reference material and assets.

- Protect the central repository and require review and ownership.
- Define clear activation descriptions, prerequisites and observable outcomes.
- Keep shared procedures generic; retain application-specific commands and
  conventions in the target repository's instructions/configuration.
- Select role-specific skill sets, with common skills shared where appropriate.
- Pin approved versions and record them in each execution's metadata.
- Evaluate actual outputs, including incorrect activation and failure cases.
- Skills are guidance, not a security boundary. Enforce restrictions through
  identities, tool permissions, sandboxing, approvals and CI controls.

## Option A: file-based distribution

```text
Central GitHub skills repository
             |
       Review and CI
             |
    Immutable role-specific bundles
             |
       ACA job initialization
             |
    Verify and extract approved content
             |
       Start agent session
```

Possible delivery mechanisms:

- Bake the approved skills into each agent image during CI. This is a simple,
  reproducible first PoC, but skill updates require rebuilding the images.
- Publish immutable bundles to private Azure Blob Storage. Each job downloads
  its pinned bundle using managed identity before creating the agent session.
- Download from GitHub using a narrowly scoped factory credential.

For downloaded bundles, verify the approved version/digest, extract safely,
check required files and stop initialization if required skills are unavailable.
Do not silently use arbitrary "latest" content or overwrite repository-owned
skills. A digest only establishes integrity relative to a trusted manifest.

The bootstrap belongs in the worker's entrypoint or application initialization:
after preparing the target repository and before starting the agent session.
It is deterministic application code, not a prompt asking the agent to install
its own instructions.

Copilot SDK supports local skill directories. Illustrative TypeScript session
configuration, using an existing client and permission handler:

```typescript
const session = await client.createSession({
    skillDirectories: [skillsDirectory],
    onPermissionRequest: permissionHandler,
});
```

The test agent needs its framework's native skills loader, or a custom adapter
if it has no native support.

## Option B: Foundry Toolboxes

This is the most recently discussed option. It has not been selected as a final
decision.

```text
Central GitHub skills repository
             |
    CI publishes immutable skill versions to Foundry
             |
       +-----+----------------------+
       |                            |
 Testing Toolbox               Coding Toolbox
       |                            |
 Test ACA job                 Copilot SDK ACA job
       |                            |
 Framework skills loader      SDK skills integration
```

The agents remain ACA jobs. Adopting Toolbox does not require migrating their
execution into Foundry Agent Service.

### Publication

1. CI creates skill versions in a Foundry project.
2. CI attaches the appropriate skills to role-specific toolbox versions.
3. Validate the candidate release before publishing/promoting it.
4. Configure jobs with approved toolbox versions and pinned skill references.

Skills attached to a toolbox must be in the same Foundry project. References
without explicit skill versions can follow the skill's default version.
Pinning only a toolbox version is therefore not sufficient for reproducibility
if its skill references remain floating.

### Runtime

1. Each ACA job obtains an Entra token using its managed identity.
2. The identity requires the appropriate Foundry authorization. Confirm the
   minimum supported scopes/roles rather than assuming toolbox-level isolation.
3. Its skills integration connects to the configured toolbox MCP endpoint.
4. `resources/list` advertises attached skills and their metadata.
5. `resources/read` retrieves selected skill instructions on demand.
6. The agent uses separately authorized tools to carry out the workflow.

The documented Foundry token scope is `https://ai.azure.com/.default`.
Refresh tokens as necessary; do not embed credentials in prompts or logs.

Toolbox skills are MCP resources, not ordinary entries in `tools/list`.
Automatic loading requires support for MCP Resources and the skills discovery
extension. Ordinary MCP tool support is not sufficient.

Toolbox serves skill content; it does not automatically execute bundled scripts
inside an ACA job. Supporting files, local paths and execution dependencies need
explicit handling.

Separate testing/coding toolboxes organize the catalogs but are not, on their
own, proof of an authorization boundary.

### Copilot SDK integration choices

**File-based bridge:** discover/download approved skill packages, materialize
their files locally and configure `skillDirectories`.

**On-demand bridge:** implement a Copilot SDK `skillProvider`, mapping:

| SDK operation | Toolbox integration |
|---|---|
| `listSkills` | MCP resource discovery, filtered to approved skills |
| `readSkill` | Read the matching skill resource and return its instructions |

This is a proposed adapter, not an already implemented or verified integration.
Handle metadata mapping, authentication/refresh, version consistency, caching,
resource files and error behavior explicitly.

Copilot SDK's custom skill-provider API is documented as **experimental**.
Foundry Toolbox skill discovery is documented as **preview**.
Do not assume that adding the toolbox to the SDK's MCP server configuration
automatically integrates its skills.

For the test agent, Microsoft documents an Agent Framework toolbox-skills
provider/sample. Applicability depends on the framework and language actually
chosen for that agent.

## Why consider Toolbox?

- Centrally hosted, versioned skills and potentially tools at the same endpoint.
- Azure-authenticated access from ACA workloads.
- Skill releases can be managed separately from application images.
- Multiple agent implementations can consume the same published content,
  provided each has a compatible skills integration.

Trade-offs include preview/experimental dependencies, runtime availability and
latency, authentication/networking, and adapter work. File-based distribution
remains a simpler alternative.

Neither approach guarantees guardrail compliance or task success.
No Rulebooks availability or Ignite GA date was confirmed.

## Suggested next-session objective

Design a bounded PoC for **Foundry Toolbox to Copilot SDK skill consumption**,
then address the test-agent framework.

Decisions required:

1. Languages and SDK/framework versions for both agents.
2. File-based bridge versus experimental on-demand provider.
3. Skill selection, authorization boundaries and version-pinning policy.
4. Handling of scripts and supporting resources.
5. Failure behavior, caching and update/rollback strategy.

Use a few harmless skills. Demonstrate fresh-job discovery, appropriate
activation, supporting-resource access, pinned-version behavior, denied access
and failure when required content cannot be loaded. Verify outcomes rather
than relying on the agent's self-reported success.

No Azure provisioning, repository changes or new credentials should be assumed
authorized by this handoff. Keep the existing demo repository/deployments
separate.

## Documentation checked during this discussion

- [GitHub Agent Skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [Copilot SDK skills and experimental providers](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/skills)
- [Foundry skills and Toolbox discovery](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/skills)
- [Create and manage Foundry toolboxes](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)
- [Agent Framework Toolbox skills sample](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/csharp/hosted-agents/agent-framework/foundry-toolbox-mcp-skills)
- [GitHub CLI skill installer](https://cli.github.com/manual/gh_skill_install)

The GitHub CLI installer was discussed for native coding-agent environments;
it is not a requirement for these custom ACA jobs. Its documented skill support
is public preview and requires GitHub CLI 2.90.0 or later.

Recheck preview status and SDK signatures before implementation.
