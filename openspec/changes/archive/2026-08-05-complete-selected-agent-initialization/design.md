## Context

See `proposal.md` for motivation and the two capability deltas for accepted behavior. Initialization currently creates or validates neutral user state and then calls the native-hook configuration path. Complete global workflow installation already composes managed ZPP skills, native hooks, generated OpenSpec skills, and persistent-default upgrades, but its public orchestration applies the plan directly and always includes workflow-install profile semantics.

The corrected initialization outcome must reuse the same projection ownership, OpenSpec generation, compatibility, and transaction guarantees while preserving initialization's stronger rule that an existing valid user-owned default profile is not additively rewritten.

## Goals / Non-Goals

**Goals:**

- Share one complete selected-agent global integration planner between initialization and global workflow installation.
- Keep the selected agents' hook, ZPP bundle, and OpenSpec projection changes in one preflighted mutation transaction.
- Preserve compatible content, replace intact outdated managed projections, and reject unmanaged or modified collisions.
- Keep initialization's existing neutral-state and user-owned default-profile behavior.

**Non-Goals:**

- Remove or rename `zpp workflow install`, `zpp update`, or any workflow lifecycle option.
- Discover or maintain agents not selected during initialization.
- Change repository-local skill behavior, agent-native roots, manifests, generated OpenSpec content, or projection version rules.
- Install or upgrade the ZPP or OpenSpec executables.

## Decisions

### Extract complete selected-agent integration planning from workflow command application

Separate the existing global workflow integration composition into a reusable planning boundary that accepts the selected agents and a profile-mutation policy. Both initialization and global `workflow install` will use the same hook, managed-skill, and OpenSpec planners before one application step.

Global workflow installation will retain its additive persistent-default upgrade policy. Initialization will disable that additive upgrade after neutral state is initialized, preserving any existing valid default byte-for-byte.

Calling the workflow CLI command from initialization was rejected because it couples command presentation, reporting, current-directory comparison, and profile policy to an internal setup operation. Reimplementing the projection logic inside initialization was rejected because it would create a second ownership and atomicity path.

### Apply install compatibility semantics to explicitly selected agents

Initialization will use the established global install classification for each selected projection: absent installs, compatible skips, intact outdated managed state replaces, and conflicts reject. OpenSpec projections retain their detected-version behavior and isolated generation boundary.

Leaving outdated managed projections unchanged was rejected because an older bundle may itself be missing a newly required permanent skill, contradicting complete selected-agent setup. Broad discovery was rejected because `zpp update` owns maintenance for agents the user did not select.

### Preserve the existing two-phase initialization boundary

Initialization will continue to establish valid neutral ZPP user state before selected-agent setup. It will then construct and apply one complete transaction across every selected agent surface. A selected-agent failure may therefore leave newly initialized neutral user state in place, matching current bootstrap behavior, but cannot partially change any selected agent.

Rolling neutral state and external OpenSpec generation into a single filesystem transaction was rejected because existing initialization intentionally has an independently valid neutral-state outcome and current public scenarios expose that boundary.

### Keep selection mechanisms behaviorally equivalent

Explicit repeated `--agent` values and agents returned by the interactive selector will feed the same complete setup path. Empty submission, cancellation, and noninteractive invocation without selections will not invoke integration planning.

Giving explicit and interactive selections different setup outcomes was rejected because the selection mechanism is not a product-level scope distinction.

## Risks / Trade-offs

- [OpenSpec is unavailable or generation fails during selected initialization] -> Fail before any selected agent surface changes, retain only valid neutral user state, and report the dependency failure.
- [Initialization becomes more expensive for selected agents] -> Preserve compatible managed and generated projections byte-for-byte and skip generation when the recorded OpenSpec version matches.
- [Shared planning accidentally changes workflow-install profile behavior] -> Keep profile mutation an explicit caller policy and cover both initialization preservation and workflow-install additive upgrade in focused tests.
- [A late conflict exists for one of several selected agents] -> Merge all selected-agent plans before applying any of them and verify atomic preservation in BDD and unit tests.

## Migration Plan

1. Extract the reusable complete global integration planner without changing existing workflow-install behavior.
2. Route explicit and interactive initialization selections through that planner with default-profile mutation disabled.
3. Update help and documentation to describe complete selected-agent setup.
4. Verify absent, compatible, outdated, conflicting, multi-agent, empty-selection, and no-selection outcomes.

Rollback restores hook-only selected initialization. Skill projections already created by a successful corrected initialization remain valid managed global workflow state and can continue through the existing workflow or top-level update lifecycle.
