# Implementation Brief: Dynamic Skills Platform for an Agentic Software Factory

## 1. Context

We are building an autonomous software factory for Electrolux, running in Azure Container Apps Jobs.

The factory processes change requests from ServiceNow and operates across potentially hundreds of existing application repositories.

Each change request creates a new execution of a specialised agent team consisting of:

- Architect
- Planner
- Coder
- Reviewer
- Tester

The agents autonomously inspect existing code, plan changes, implement features, review code and execute tests.

Human approval is required before committing, pushing or deploying changes.

Application owners interact with the factory through change requests and approval workflows. They do not configure agents or manage skills.

**Our task is to build the skills infrastructure that enables these agents to discover and use appropriate skills dynamically.**

## 2. Architectural decisions

Use two repositories:

### Repository A: `software-factory`

Contains the factory implementation, agent definitions, orchestration and Azure infrastructure.

Extend this repository with the skills integration components.

### Repository B: `software-factory-skills`

A dedicated repository containing reusable skills following the open Agent Skills specification.

This repository is the authoritative source for skills.

Skills must be independently maintained, tested and versioned without requiring changes to the factory's agent implementations.

### Important principles

1. Skills must not be hardcoded into individual agent implementations.
2. Agents must be able to work with repositories unknown at deployment time.
3. Skills must be selected dynamically based on the agent's role, target repository and task.
4. Prefer native GitHub Copilot skill capabilities wherever supported.
5. Do not introduce unnecessary infrastructure.
6. Design for future integration with Microsoft Foundry Toolboxes.
7. Skill versions must be reproducible across an individual factory execution.
8. The platform team owns the skills lifecycle.
9. Target application repositories must not require modifications to participate.

## 3. Skills repository

Create `software-factory-skills`.

Use the standard Agent Skills directory structure.

Implement an initial collection of reusable skills covering:

**General engineering**
- Architecture analysis
- Implementation planning
- Code review
- Test strategy
- Legacy code analysis

**Technology-specific**
- .NET development
- Java development
- Python development
- API development
- Database changes

These should be useful, working skills rather than placeholder descriptions.

Each skill should include:

- A clear description of when it should be used
- Instructions following the Agent Skills specification
- Supporting resources where appropriate
- Tests validating its expected behavior

Create a machine-readable catalog containing additional factory-specific metadata:

- Skill identifier
- Version
- Applicable agent roles
- Applicable technologies
- Prerequisites
- Dependencies
- Compatibility requirements

Keep the catalog separate from the standard skill format so skills remain portable.

Implement CI validation and versioned releases.

## 4. Dynamic skill discovery

Implement a skill discovery mechanism in `software-factory`.

When a new feature execution starts:

1. Identify the target application repository.
2. Inspect the repository to determine its technology stack and relevant characteristics.
3. Identify the agents participating in the execution.
4. Discover available skills from the central skills repository.
5. Select appropriate skills based on role, technology and task.
6. Resolve and pin the selected skill versions for the execution.
7. Make the selected skills available to each agent.

For example:

A ServiceNow request targets an existing .NET application.

The factory discovers that the application uses .NET and SQL Server.

The architect receives architecture-analysis and relevant technology skills.

The coder receives .NET development and database-change skills.

The reviewer receives code-review and relevant technology skills.

The tester receives test-strategy and relevant technology skills.

The agents should still be able to discover and activate individual skills when relevant during their work.

Do not assume every skill must be loaded into the model context immediately.

## 5. GitHub Copilot integration

Investigate and use the native skill capabilities supported by the actual GitHub Copilot runtime used in the factory.

Important: distinguish between:

- GitHub Copilot CLI
- GitHub Copilot SDK
- GitHub Copilot cloud coding agent

Do not assume that features supported by one runtime are available in another.

Inspect the existing factory implementation and identify the actual runtime for each agent.

Use the simplest supported integration.

Where native discovery or loading is insufficient, implement a small adapter that materializes selected skills in the format expected by the runtime.

Avoid creating a custom skill execution engine if the existing runtime already supports the required functionality.

## 6. Skill distribution architecture

Start with GitHub as the source and distribution mechanism.

Evaluate the simplest practical approach for retrieving versioned skills from the central repository during an ACA job execution.

The implementation must support:

- Automated retrieval without human interaction
- Authentication to private repositories
- Version pinning
- Reproducibility
- Multiple concurrent factory executions
- Failures and retries
- Minimal startup overhead

Introduce a `SkillResolver` abstraction so the distribution mechanism can change independently of the agents.

Initially implement a GitHub-based resolver.

Design the interface to support future implementations such as:

- Microsoft Foundry Toolbox
- Azure Container Registry OCI artifacts
- Azure Blob Storage

Do not implement all these alternatives now.

Document the trade-offs and explain when another distribution mechanism would be preferable.

## 7. Execution consistency

Each feature execution must have a unique execution identifier.

Generate a resolved skills manifest containing:

- Execution identifier
- Target repository and commit
- Participating agent roles
- Selected skills
- Exact skill versions or immutable references
- Relevant integrity information

All agents participating in the same execution must use the same resolved skill versions where they share a skill.

A new skills release must not unexpectedly change an execution already in progress.

Persist the manifest so the execution can be audited and reproduced.

## 8. Security and governance

The factory operates on existing enterprise repositories.

Implement appropriate controls:

- Authenticate using workload identity or appropriately scoped GitHub credentials.
- Restrict which skills can be loaded.
- Treat target-repository content as untrusted input.
- Do not automatically execute arbitrary scripts discovered in target repositories.
- Separate skill instructions from enforced security policies.
- Preserve human approval gates.
- Record which skills were selected and activated.

Repository-specific instructions can provide application context, but must not override factory security controls.

Skills must not be able to bypass approval or authorization requirements.

## 9. Testing

Create an end-to-end local test using a sample existing application repository.

Simulate a change request and verify that:

1. The factory identifies the target technology stack.
2. Relevant skills are discovered.
3. Different agent roles receive appropriate skills.
4. Skills are successfully loaded by the actual agent runtime.
5. Skills activate when relevant.
6. Irrelevant skills are not unnecessarily activated.
7. The same skill versions are used throughout the execution.
8. A new skills release does not affect an active execution.
9. Missing or unauthorized skills fail safely.
10. Execution metadata records the skills used.

Tests should verify actual behavior, not simply that an agent claims to have used a skill.

## 10. Deliverables

Implement:

**In `software-factory-skills`:**
- Repository structure
- Initial working skills
- Skills catalog
- Validation and release pipeline
- Documentation

**In `software-factory`:**
- Repository profiler
- Skill discovery and selection
- GitHub skill resolver
- Runtime integration
- Execution manifest
- Logging and error handling
- Integration tests

Also provide:

1. Architecture documentation
2. Local development instructions
3. Deployment configuration
4. An end-to-end demonstration
5. A comparison of GitHub-native distribution, Foundry Toolbox and OCI/Blob distribution

## 11. Implementation approach

Before writing code:

1. Inspect the existing factory repository.
2. Identify its languages, frameworks, agent runtimes and orchestration approach.
3. Verify the current GitHub Copilot skill APIs against official documentation.
4. Identify what can be reused.
5. Present a concise implementation plan.

Then implement the solution incrementally.

**Do not rebuild existing factory functionality or introduce a new orchestration framework.**

Do not assume that a dedicated skill registry service is necessary.

Prefer the simplest implementation that satisfies the requirements while preserving the ability to adopt Foundry Toolbox later.

## 12. Definition of done

The implementation is complete when:

- A new feature execution can discover relevant skills from the central repository.
- Skills are selected based on agent role and target repository.
- The agents successfully consume those skills using their actual runtimes.
- Skills can be updated independently of factory code.
- Executions use reproducible skill versions.
- Tests demonstrate the end-to-end behavior.
- The distribution implementation can be replaced without changing individual agent implementations.

The goal is a **reusable, dynamically extensible skills platform for an autonomous enterprise software factory**, not merely a repository containing Markdown instructions.