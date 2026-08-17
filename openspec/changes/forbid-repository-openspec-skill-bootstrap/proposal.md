## Why

The consolidated workflow names the six installed OpenSpec operation skills but
does not explicitly forbid an agent from running `openspec init` or creating a
project-local skill installation when those operations are missing. ZPP already
owns OpenSpec skill generation and user-scope projection, so workflow-local
bootstrap would create a second lifecycle authority and mutate the target
repository unexpectedly.

## What Changes

- Prohibit every ZPP workflow run from invoking, authorizing, or accepting
  `openspec init` or any repository-local generation, installation, projection,
  repair, or vendoring of OpenSpec operation skills.
- Require the workflow to consume only the six already installed operation
  skills supplied through ZPP's agent integration.
- Block the current stage when a required operation skill is absent, invalid, or
  stale, and direct the owner to root `zpp init` for a new integration or
  `zpp sync` for an existing integration instead of self-healing the repository.
- Preserve ordinary repo-local OpenSpec planning: creating and updating
  `openspec/` changes and specifications is allowed and is not skill bootstrap.
- Preserve ZPP's generation implementation: `zpp init` and `zpp sync` may invoke
  OpenSpec only inside disposable temporary repositories and may project the
  resulting exact inventory only through Agent Router into user scope.
- Correct the provisioning contract so first-time creation belongs to
  `zpp init`, repair belongs to `zpp sync`, and neither authority is attributed
  to workflow runs or project-scope lifecycle commands.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Add a non-bypassable prohibition against
  repository-local OpenSpec skill bootstrap and a blocking handoff to ZPP's
  lifecycle commands.
- `openspec-skill-provisioning`: Reconcile the existing initialization-only
  wording with the accepted initialization-versus-synchronization ownership
  split and make disposable generation plus user-scope projection exclusive to
  ZPP.

## Impact

- `src/zpp/artifacts/skills/workflow/zpp-workflow/SKILL.md`
- `openspec/specs/consolidated-workflow-skill/spec.md` during specification formation
- `openspec/specs/openspec-skill-provisioning/spec.md` during specification formation
- No runtime, CLI, dependency, Gherkin, BDD, utility, TDD, or product-wiring changes; current implementation and tests already establish disposable generation and user-scope projection

## Unresolved — Do Not Assume

None.
