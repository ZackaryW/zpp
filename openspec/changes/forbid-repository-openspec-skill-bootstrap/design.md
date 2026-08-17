## Context

ZPP detects the local OpenSpec CLI, invokes its generator inside a disposable
temporary repository, validates the exact six-operation inventory, and projects
those skills through Agent Router into each selected agent's user scope. Root
`zpp init` creates a new integration and root `zpp sync` repairs an existing one.
The generated operation skills themselves do not invoke `openspec init`.

The consolidated workflow names those operation owners but does not say what to
do if one is missing, invalid, or stale. Without an explicit boundary, an agent
could attempt to self-heal by running `openspec init` in the product repository,
creating project-local `.codex/skills`, `.claude/skills`, `.pi/skills`, or
`.kimi/skills` content outside ZPP's ownership and projection contracts.

The provisioning specification also predates the accepted lifecycle split: it
says only `zpp init` may regenerate or project OpenSpec skills, while current
code and durable decision `fc44ebd:1` assign repair to `zpp sync`. Its separate
forced-initialization requirement also requires the removed `zpp init --force`
mode even though current code and the canonical product-home lifecycle assign
forced owned repair to `zpp sync --force`.

## Goals / Non-Goals

**Goals:**

- Make repository-local OpenSpec skill bootstrap impossible under workflow
  authority.
- Keep skill generation and projection exclusively inside ZPP's lifecycle,
  disposable-generation, Agent Router, and user-scope boundaries.
- Block truthfully when an operation owner is unavailable rather than allowing
  the workflow to install or repair it.
- Preserve ordinary repo-local OpenSpec planning artifacts and operations.
- Reconcile the provisioning specification with initialization creating and
  synchronization repairing integrations.
- Remove the obsolete forced-initialization authority without weakening
  ownership-safe forced synchronization.

**Non-Goals:**

- Prohibit repo-local `openspec/` proposals, changes, specifications, or archives.
- Remove ZPP's use of `openspec init` inside disposable temporary repositories.
- Add project-scope lifecycle support for generated OpenSpec skills.
- Change the six-skill inventory, Agent Router ownership, CLI behavior, or
  executable generation implementation.
- Add tests that pin prose already governed by canonical specifications.

## Decisions

### Workflow runs never bootstrap operation skills

The packaged workflow will state that it must consume the exact installed
OpenSpec operation skills and must never invoke `openspec init`, generate or
vendor a skill tree, project operation skills, or repair them. This prohibition
applies regardless of whether the proposed destination is the target repository,
an adjacent worktree, a project-scoped agent directory, or a workflow-created
temporary directory. Only the ZPP lifecycle owns generation.

Restricting only writes under the current repository was rejected because a
workflow could evade the ownership boundary by generating elsewhere and then
copying or projecting the result.

### Missing operation owners block the stage

If a required operation skill is absent, unreadable, invalid, stale, or requests
local initialization as a prerequisite, the current stage remains blocked. The
workflow reports the exact skill and directs the owner to root `zpp init` when no
integration exists or root `zpp sync` when an integration already exists. It
does not invoke those lifecycle commands automatically, because workflow
progression does not grant external integration-mutation authority.

Continuing with a generic OpenSpec CLI command was rejected because it bypasses
the exact component operation owner. Automatically running ZPP lifecycle was
rejected because it mutates user-scope agent integrations outside the stage.

### Planning state remains repository-local

The prohibition covers skills and their lifecycle, not OpenSpec product state.
Installed operations may create, update, validate, synchronize, and archive the
repository's `openspec/` planning artifacts. This distinction prevents an
over-broad rule from disabling the product workflow it is meant to protect.

### ZPP initialization and synchronization share exclusive provisioning ownership

The provisioning requirement will distinguish first-time creation from repair:
`zpp init` generates and projects the complete integration for an uninitialized
agent; `zpp sync` freshly generates the current inventory and safely reconciles
an installed agent. Both generate only in disposable repositories and project
only through Agent Router into user scope. No workflow or project-scope command
inherits that authority.

### Forced repair belongs only to synchronization

The obsolete `Forced complete initialization` requirement will be removed.
`zpp init` remains limited to agents carrying no ZPP projection and exposes no
force mode. An installed integration that requires complete owned reprojection
uses `zpp sync --force`, which continues to preserve unmanaged or mismatched
destinations through Agent Router.

Keeping both force paths was rejected because it would restore two lifecycle
commands with the same repair responsibility and contradict the accepted
create-versus-repair split.

## Risks / Trade-offs

- **A missing skill now stops work instead of self-healing** → Report the exact
  missing owner and the appropriate ZPP lifecycle handoff.
- **“OpenSpec initialization” can be confused with creating planning state** →
  Name skill generation/projection explicitly and affirm repo-local planning.
- **A stale skill may not be independently detectable during every run** → Apply
  the block whenever stale or invalid evidence is observed; never claim a hidden
  freshness check.
- **The provisioning title retains older terminology** → Modify its complete
  normative content without inventing a rename-only delta; the requirement will
  explicitly distinguish initial creation from synchronization repair.

## Migration Plan

1. Add the workflow prohibition and blocking lifecycle handoff.
2. Reconcile both affected canonical requirements.
3. Remove the obsolete forced-initialization requirement from the canonical
   provisioning specification.
4. Validate the prose/specification artifacts and complete repository gates
   without adding BDD or TDD.
5. Archive the change; existing user-scope projections require no migration.

Rollback removes the workflow prohibition and restores the prior provisioning
wording. It does not change existing agent projections or repository planning
artifacts.

## Open Questions

None.
