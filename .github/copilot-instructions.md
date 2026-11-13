# Skills-developer workflow for this PoC

These instructions apply to authoring in `factory-skills`, not to the
proposal-only agents in `ai-factory`.

For a concrete skill-change request, complete the authoring and delivery work
without asking the user to edit JSON, create a branch/PR, commit, push or approve
a Foundry deployment. Questions and walkthroughs do not authorize a change.
Use normal CLI tool permissions; do not enable blanket approvals.
Manual skill edits and direct pushes are also supported; CI owns default
version increments, not this instruction file.

## Authoring

- Read the existing skill, supporting resources, catalog entry and evaluation.
  Implement the requested behavior using portable instructions and relative links.
- Maintain catalog applicability metadata when the request requires it. CI
  compares skill-file hashes with the last promoted release and commits missing
  patch-version increments automatically. Do not pre-bump an existing skill just
  to satisfy CI; an explicit higher minor/major/patch version is preserved.
  New skills still need a valid catalog entry, normally starting at `1.0.0`.
  Foundry assigns its own service version numbers.
- Preserve existing roles, tasks, technologies, prerequisites, dependencies and
  compatibility unless the requested behavior changes applicability. For new
  skills or explicit applicability changes, derive metadata from the request and
  the catalog schema. Do not assign every role or technology for convenience;
  clarify genuinely ambiguous intent rather than inventing it.
- Maintain `evaluations.json` automatically: keep a realistic positive task,
  specific observable expected outcomes matching the requested behavior, and an
  irrelevant negative task. Preserve useful checks unrelated to the change.
  Do not weaken expectations merely to make a run pass.
- Skills cannot grant tools or credentials. Do not change factory
  `permitted_skills`, worker permissions, identities, Azure resources or deployment
  configuration as part of ordinary skill authoring.

## Check and deliver

- Work against current `origin/main` without overwriting local work. Preserve
  unrelated user changes. Do not force-push, reset or rewrite history.
- Validate the library with `python -m tools.skills validate` and run the existing
  tests, lint and formatting checks. Markdown-only edits may initially lack a
  version bump: the main-branch pipeline supplies it before strict validation.
  Repair failures caused by the requested change before publishing.
- By default, commit only the requested changes and push directly to `main` in
  this repository. A branch or PR is optional only when the user requests one.
  This PoC authorization does not cover commits or pushes in `ai-factory`.
- Follow the automatically triggered `Publish Foundry skills` run through
  completion. It must not require a deployment approval. If publishing fails,
  investigate; never bypass checks, silently change credentials or delete old
  versions to make it pass.
- CI may add a catalog-only `github-actions[bot]` commit to `main`. After a
  successful run, fetch and fast-forward a clean local checkout to that commit
  before further edits. Never overwrite local changes to synchronize.
- Return the successful Actions run and versioned binding release links. Report
  incomplete or blocked work plainly; a local commit or green unit suite alone
  does not prove publication.

CI checks structure, versions and distribution integrity. AI-maintained
evaluation expectations are not proof of model behavior. Claim behavioral
verification only after an actual factory run demonstrates the outcomes with
native SDK activation evidence. Existing runs retain their pins; new runs must
use the published binding.
