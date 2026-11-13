# Factory skills

Portable development skills for `katarinasvedman-ms/ai-factory`. This repository
owns skill content and releases; the factory owns orchestration, selection,
runtime integration, and authorization.

See [the implementation walkthrough](docs\implementation-walkthrough.md) for
actual discovery-to-activation code paths and retained Foundry execution evidence.

The initial catalog contains architecture analysis, implementation planning,
code review, test strategy, legacy analysis, .NET, Java, Python, API development,
and SQL Server database changes. Skills contain useful procedures, not tool
permissions. Supporting resources are loaded only when relevant.

## Local development

Requires Python 3.13 and pip 25.1 or later. From this repository in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -e . --group dev
.\.venv\Scripts\python.exe -m tools.skills validate
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check tools tests
.\.venv\Scripts\python.exe -m ruff format --check tools tests
.\.venv\Scripts\python.exe -m tools.skills build --output .artifacts\release-demo
```

Choose a new output directory for each build. The builder produces a directory
and deterministic ZIP containing `catalog.json`, `release.json`, and skills.
`release.json` hashes the catalog and every file in every skill, including
references. These digests establish integrity only relative to a trusted source;
they are not signatures or authorization.

`requirements.lock` contains resolved dependency constraints. Keep it aligned
with `pyproject.toml`; deliberately review SDK/API dependencies on updates.

## Authoring and evaluation

Each `skills\<id>\SKILL.md` uses the open Agent Skills format: unquoted YAML
`name` and `description`, followed by procedural Markdown. Put optional
resources under that skill's folder and use relative links. Do not put
factory-specific metadata into the portable format.

Add role, technology, task, prerequisite, dependency, and runtime compatibility
metadata to `catalog.json`. Add a positive task, expected observable outcomes,
and an irrelevant negative task to `evaluations.json`. Increment the skill's
semantic version whenever instructions or resources change.

Validation checks the schema, names, frontmatter, resources, directory coverage,
dependencies, and evaluation fixture coverage. Unit tests check reproducibility
and failures; they do not prove model behavior. The factory's opt-in live
evaluation verifies native SDK activation, a supporting-resource read, concrete
.NET compatibility evidence, proposal creation, and non-activation of available
but irrelevant API/database skills. The other behavioral rubrics remain inputs
for expanded live evaluation, not claims of successful evaluation.

Target-specific commands and conventions belong in application context.
Never put credentials, automatic script execution, or approval bypasses in skills.

## GitHub releases

The validation workflow checks pull requests and `main`. PRs require a version
increment for changed skill files. A reviewed `v*` tag builds a ZIP, writes its
SHA-256, and publishes a GitHub release. Protect `main`, tags, and the
`skills-release` environment; require CODEOWNERS review. These settings must
be enabled by a repository administrator; adding workflow files does not enable
branch protection.

The factory's GitHub resolver retrieves the source tree at an operator-approved
full commit SHA, not `main`, a floating tag, or an unbound release asset. Release
ZIPs are useful for mirroring/audit. Resolve an approved tag to its commit
outside the worker before configuring a new execution.

## Foundry publication

An alternative distribution path uses an existing Foundry project. The explicit
publication command creates immutable skill versions, then a toolbox version
with explicit version references. It preserves all supporting files. It does
not provision a project, create credentials, or promote an existing toolbox's
default version. A brand-new toolbox's first version becomes its default as
part of the service's normal behavior.

Install the optional publisher dependencies and use an existing authorized
Azure login or workload identity:

```powershell
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -e ".[foundry]"
.\.venv\Scripts\python.exe -m tools.publish_foundry `
  --endpoint "https://YOUR-ACCOUNT.services.ai.azure.com/api/projects/YOUR-PROJECT" `
  --toolbox factory-skills --output .artifacts\foundry-binding.json --publish
```

Do not pass credentials on the command line. In environments where a working
Azure CLI login should be used explicitly, set
`$env:AZURE_TOKEN_CREDENTIALS = 'AzureCliCredential'` for that process.
The publisher does not retry POST operations automatically: if interrupted,
some immutable versions may already exist. Inspect those versions before
rerunning; do not delete existing skills to retry a release.

### GitHub-to-Foundry release flow

The `Publish Foundry skills` workflow runs automatically on a push/merge to
`main`, or manually on `main` for recovery. Pull requests run validation only
and cannot obtain the publishing identity.

1. Edit a skill or supporting resource, increment its version in `catalog.json`,
   update `evaluations.json` when behavior changes, and push a PR.
2. CI checks content, version increments, tests, lint, formatting and the
   reproducible source package.
3. Merge to `main`. In **Actions > Publish Foundry skills**, approve the
   `foundry-publish` environment under **Review deployments**.
4. The publisher uses GitHub OIDC, without a stored Azure secret. It uploads
   changed skill packages once and creates only affected `<role>-skills`
   Toolbox versions. Shared skills use the same pin across every consuming role.
   The first release uploads all skills to establish the automated baseline.
5. Before promotion, CI downloads every pinned skill package and checks all
   file hashes against the checkout, then checks each role Toolbox's exact
   references and absence of tools. A failure prevents release promotion.
6. CI creates a versioned `foundry-*` GitHub release containing
   `role-bindings.json`, source commit, content hashes, worker identity IDs,
   and the uploaded-skill/changed-toolbox lists. The Actions summary links to it
   and provides the exact download command.

Unchanged versions are reused from the previous successful `foundry-*` release;
they are still verified remotely. The single-role `--toolbox` command above is
the original all-catalog publisher, not the role-aware CI path. For role
publication, the workflow uses `--role-identities`, `--source-commit` and, after
the first release, `--baseline`. Do not use the one-off
`ai-factory\tools\setup_role_isolation.py` bootstrap script for subsequent releases.

Publication jobs are serialized, reject superseded main commits, and never
automatically retry mutations or delete old versions. A failed publication can
leave unreferenced immutable versions; inspect the run and Foundry before
retrying. Its previous promoted binding remains usable. Distribution checks
verify exact bytes and references, not model behavior or native SDK activation.

### Using a promoted release in the factory

The new version is available through the exact pinned endpoints in the release
binding. This does **not** change Foundry's unversioned service defaults or
existing execution manifests. After downloading the binding with the Actions
summary's command, prepare a new execution from the `ai-factory` directory:

```powershell
.\.venv\Scripts\ai-factory.exe prepare --source foundry --skill-mode provider `
  --foundry-binding <downloaded-role-bindings.json> `
  --target .\tests\fixtures\orders `
  --request .\examples\request.json --policy .\examples\provider-policy.json
```

Keep the downloaded file pinned for that execution; to roll back, prepare a new
execution with the previous release's binding. New skills must also be explicitly
permitted in the factory policy. Publisher credentials are separate from worker
credentials and Copilot model authentication; CI does not distribute worker
private keys or run model sessions. Yesterday's temporary local-test keys were
removed, so local identity-isolated model runs require new worker credentials.

### GitHub environment configuration

The `foundry-publish` environment requires an approval and allows only the `main`
branch. Its Azure application has a federated credential with issuer
`https://token.actions.githubusercontent.com`, audience
`api://AzureADTokenExchange`, and subject
`repo:katarinasvedman-ms/factory-skills:environment:foundry-publish`.
It receives Foundry User only at the existing project's scope.

Configure these environment variables, not secrets:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
`FOUNDRY_PROJECT_ENDPOINT`, and `FOUNDRY_ROLE_IDENTITIES`.
The last is a JSON object mapping each existing role to `type`, `tenant_id`,
`client_id` and `principal_id` of its worker identity. Protect `main` through
repository rules as appropriate; workflow files alone do not enable protection.
Separate toolboxes are not an authorization boundary; confirm actual Foundry
RBAC scope. The publisher's project-level Foundry User grant is broader than
skill-read access and is not assigned to a subscription or resource group.

## PoC state

On 2026-11-12, ten skills and the `factory-skills` toolbox version `1` were
published to the existing, explicitly authorized `factory-skills` Foundry
project. The generated binding is retained in
`.artifacts\foundry-binding.json`, not embedded in agent code. Real resource
discovery, pinned package retrieval, and SDK consumption were verified.

The skills repository's initial push and OIDC pipeline activation were explicitly
authorized for the demo. This does not authorize committing or pushing the
sibling factory repository.
