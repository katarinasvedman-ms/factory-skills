# Factory skills

Portable development skills with independent authoring, validation and
versioned publication. Skills describe useful procedures; they do not grant
tools, credentials or permission to execute commands.

This repository owns content, catalog metadata, evaluation expectations and
releases. Consumers own task selection, runtime integration, authorization and
execution evidence. The reference consumer is
[`ai-factory`](https://github.com/katarinasvedman-ms/ai-factory); the skill format
is not specific to that runtime or a particular customer.

## Status and scope

**The bounded skill-lifecycle PoC is demonstrated:** author a change, publish it
through CI, load the pinned revision through native SDK activation, observe the
changed reporting behavior, preserve existing execution pins, and roll back.
This does not prove general quality improvement or production readiness.

The reference consumer keeps the Foundry bridge as default and its experimental
on-demand provider opt-in. The SDK supplies native skill selection/loading;
our adapter connects it to Foundry. Provider allow-lists are application
filtering, not verified Toolbox-scoped Azure authorization.

The remaining proof is focused, not another broad lifecycle spike:

| Before claiming | Required evidence | Owner |
| --- | --- | --- |
| A deployed worker adopted the tested revision | A new Azure execution using the selected release binding | Consumer/runtime |
| Skills reliably improve results | Repeated relevant/irrelevant-task evaluations and grounded output checks | Skills and consumer |
| Provider is production-ready | Credential-latency remediation and long-session, refresh, interruption and availability tests | Consumer/runtime |

See [verification and limitations](docs\verification.md) for dated results,
exact release references, quality gaps and the distinction between local
evaluation and Azure adoption. Application builds/tests were not executed by
the demonstrated workers.

## Documentation

- [Scope and design principles](docs\brief.md)
- [Authoring-to-activation walkthrough](docs\implementation-walkthrough.md)
- [Ownership and consumer handoff](docs\skills-factory-handoff.md)
- [Focused remaining work](docs\implementation-plan.md)
- [Verification record](docs\verification.md)

## Local development

The documented development environment uses Python 3.13 and pip 25.1 or later.
From the repository in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -e . --group dev
.\.venv\Scripts\python.exe -m tools.skills validate
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check tools tests
.\.venv\Scripts\python.exe -m ruff format --check tools tests
.\.venv\Scripts\python.exe -m tools.skills build --output .artifacts\release
```

Choose a new build output directory each time. The deterministic directory/ZIP
includes the catalog, skills and a `release.json` of file hashes. Hashes establish
integrity relative to trusted metadata; they are not signatures or authorization.
Keep `requirements.lock` aligned with deliberate dependency changes.

## Authoring

Each `skills\<id>\SKILL.md` uses Agent Skills frontmatter (`name`, `description`)
and procedural Markdown. Put optional resources beneath that skill folder and
link them relatively. Keep application-specific commands and conventions in
application context, not shared skills.

`catalog.json` separately defines semantic version, roles, tasks, technologies,
prerequisites, dependencies and compatibility. `evaluations.json` records a
realistic positive task, observable expectations and an irrelevant negative
task. Sample applications in those fixtures are test cases, not customer
configuration.

Manual edits and direct main pushes are supported for this PoC. On the main
publication path, CI supplies missing patch increments for changed skill files;
an explicit higher version is preserved and downgrades are rejected. New skills
still need valid catalog and evaluation entries. CI does not infer applicability
or rewrite intended evaluation outcomes.

Validation checks structure, metadata, resources and evaluation coverage.
Unit tests and distribution checks do not prove model behavior. That requires
actual runtime activation evidence and grounded outputs.

## Automated Foundry publication

`Publish Foundry skills` runs on a main push or manual main dispatch:

1. Compare skill hashes with the last promoted `foundry-*` binding. Commit
   generated catalog patch increments as `github-actions[bot]` when needed.
2. Validate, test, lint, format and package the resulting commit.
3. Authenticate using GitHub OIDC. Upload changed skills once, reuse unchanged
   service pins and create only affected role Toolbox versions.
4. Download and verify pinned packages and exact Toolbox references.
5. Promote a versioned GitHub release containing `role-bindings.json`, source
   provenance, content hashes and role identity mappings.

Shared skills retain the same pin across consuming roles. Catalog semantic
versions, Foundry skill service versions and Toolbox versions are distinct.
The bot push does not recursively trigger another workflow; the current run
validates the resulting commit. Stale runs stop and pushes are never forced.
Pull before subsequent edits if CI added a catalog commit.

The demo has no required PR or deployment-approval click. This is not a
production review policy. A Toolbox version records composition, not inherently
human approval. Optional PR checks require appropriate version increments;
automatic catalog write-back is limited to the main publishing path.

Publication jobs are serialized. Mutating POST operations are not automatically
retried, and old versions are not deleted. A failure can leave unreferenced
immutable versions; inspect the run before retrying. The previous promoted
binding remains usable. A catalog commit can exist even if later checks fail.

### Environment configuration

The `foundry-publish` GitHub environment is restricted to main. Configure these
environment variables, not secrets:

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
`FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_ROLE_IDENTITIES`.

The identity map supplies `type`, `tenant_id`, `client_id` and `principal_id` per
role. Provision identities and project grants separately; ordinary skill
authoring must not change worker permissions, identities or deployment resources.
Project-level Foundry User is broader than skill-read access.

Federated trust uses issuer `https://token.actions.githubusercontent.com` and
audience `api://AzureADTokenExchange`. Match the actual Actions token subject;
the observed form includes owner and repository IDs:

```text
repo:<OWNER>@<OWNER_ID>/<REPOSITORY>@<REPOSITORY_ID>:environment:<ENVIRONMENT>
```

Do not assume the older name-only subject. Production branch, tag, environment
and ownership protections must be configured by administrators; workflow files
alone do not enable them.

### Explicit publication and source releases

The original all-catalog publisher remains available for an authorized,
existing Foundry project:

```powershell
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -e ".[foundry]"
.\.venv\Scripts\python.exe -m tools.publish_foundry `
  --endpoint "https://YOUR-ACCOUNT.services.ai.azure.com/api/projects/YOUR-PROJECT" `
  --toolbox YOUR-TOOLBOX --output .artifacts\binding.json --publish
```

This is not the role-aware CI path, which uses `--role-identities`,
`--source-commit` and a prior `--baseline`. Do not use a consumer's one-off
identity/Toolbox bootstrap script for subsequent releases.

Use an existing authorized credential; never put tokens on the command line.
For explicit local Azure CLI selection, set
`$env:AZURE_TOKEN_CREDENTIALS = 'AzureCliCredential'` for that process.
The publisher does not provision projects or change existing Toolbox defaults.
A new Toolbox's first version may become its default through service behavior.

The separate `v*` tag workflow builds a source ZIP and SHA-256 release.
Consumers using GitHub source must resolve an approved full commit SHA rather
than trust a floating branch, tag or unbound asset.

## Consumer adoption and rollback

Download and explicitly select a promoted binding for a new execution.
Publication does not update worker configuration, existing manifests, credentials
or Foundry's floating defaults. To roll back, prepare a new execution with a
previous binding. Keep policy approval (`permitted_skills`) separate from
published availability.

Publisher, worker registry and model credentials serve different purposes.
CI does not distribute worker private keys or run model sessions. Consult the
consumer's documentation for its pinned runtime, preparation command,
credential requirements and native activation evidence.
