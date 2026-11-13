# Skills-developer workflow for this PoC

These instructions apply to authoring in `factory-skills`, not to the
proposal-only agents in `ai-factory`.

For a concrete skill-change request, complete the authoring and delivery work
without asking the user to edit JSON, create a branch/PR, commit, push or approve
a Foundry deployment. Questions and walkthroughs do not authorize a change.
Use normal CLI tool permissions; do not enable blanket approvals.

## Authoring

- Read the existing skill, supporting resources, catalog entry and evaluation.
  Implement the requested behavior using portable instructions and relative links.
- Maintain `catalog.json` automatically. For an existing skill whose instructions
  or resources changed, increment the patch component relative to the published
  source baseline unless the user explicitly requests a minor/major release.
  Do not increment it repeatedly while refining the same unpublished change.
  New skills start at `1.0.0`. Foundry assigns its own service version numbers.
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
- Validate the library and version changes using `python -m tools.skills validate
  --baseline <full-origin-main-commit-SHA>`; resolve the SHA with
  `git rev-parse origin/main`, not a branch name passed as the baseline.
  Run the existing tests, lint and formatting checks. Repair failures caused by
  the requested change before publishing.
- By default, commit only the requested changes and push directly to `main` in
  this repository. A branch or PR is optional only when the user requests one.
  This PoC authorization does not cover commits or pushes in `ai-factory`.
- Follow the automatically triggered `Publish Foundry skills` run through
  completion. It must not require a deployment approval. If publishing fails,
  investigate; never bypass checks, silently change credentials or delete old
  versions to make it pass.
- Return the successful Actions run and versioned binding release links. Report
  incomplete or blocked work plainly; a local commit or green unit suite alone
  does not prove publication.

CI checks structure, versions and distribution integrity. AI-maintained
evaluation expectations are not proof of model behavior. Claim behavioral
verification only after an actual factory run demonstrates the outcomes with
native SDK activation evidence. Existing runs retain their pins; new runs must
use the published binding.
