# codespace-locking Specification

## Purpose

Defines on-demand conflict gating for concurrent OpenSpec working views while preserving canonical checkouts when isolation is unnecessary.

## Requirements

### Requirement: Explicit on-demand view claims
ZPP SHALL create a durable machine-local codespace claim only from explicit paths, an explicit workspace descriptor, or an existing active claim containing the current checkout. OpenSpec worksets SHALL NOT establish, transfer, or prove write ownership, and core locking SHALL NOT depend on editor folder discovery.

The claim SHALL cover each complete committed project checkout and the effective checkout of every external writable OpenSpec store selected by that project. A repo-local OpenSpec root SHALL be covered by its containing project checkout, reference-only stores SHALL remain unclaimed, and unclassified stores or repositories without a committed `HEAD` SHALL cause the complete request to fail without partial state.

#### Scenario: Claim a resolvable target set
- **WHEN** a user locks an explicit committed target set whose writable OpenSpec authority can be classified
- **THEN** ZPP atomically claims its complete writable closure without creating isolation, a workset projection, or an editor session

### Requirement: Separate snapshot, checkout, and instance identity
ZPP SHALL use effective physical checkout identity for exclusive active ownership and SHALL record every member's full starting commit hash as immutable snapshot provenance. File changes, new commits, and checkout movement SHALL be reported as current state without replacing the claim, changing its structural generation, or rewriting its starting snapshot.

Each codespace SHALL have a stable instance identity. An exact active effective target set SHALL resolve idempotently to that instance, while independently isolated physical checkouts MAY form a distinct instance even when they begin from the same source commits.

#### Scenario: Retain an active claim across commit movement
- **WHEN** a claimed checkout changes after acquisition and the same effective target set is inspected or locked again
- **THEN** ZPP retains the existing instance and immutable starting snapshot while reporting current checkout state separately

### Requirement: Confirmed worktree mitigation
ZPP SHALL report the complete overlapping physical checkout set and its active owning codespaces before mitigation. It SHALL create isolation only after confirmation, retain uncontested canonical checkouts, and create distinct sibling Git worktrees for conflicting projects and external governing stores from their recorded starting commits without copying uncommitted content.

ZPP SHALL reject pre-existing target paths or branches without overwrite, claim the isolated effective checkouts atomically, preserve original logical store IDs in a private registry, leave shared global registration unchanged, and keep opening the prepared codespace optional.

#### Scenario: Mitigate a conflicting writable closure
- **WHEN** a user confirms mitigation for a request that overlaps active physical checkouts
- **THEN** ZPP prepares and claims only the required isolated checkouts without changing an existing workspace or shared OpenSpec registry

### Requirement: Atomic codespace lifecycle
ZPP SHALL expose lock, add, list, status, optional open, activate, exec, unlock, cleanup, disposition, recovery, and finalize operations. Adding paths SHALL atomically replace the same instance's complete claimed target set; failure or declined mitigation SHALL leave its original claim and optional projection unchanged.

Activation and wrapped execution SHALL use the codespace's private OpenSpec registry. Unlock and forced recovery SHALL release write ownership and remove only its ZPP-owned projection while preserving generated worktrees and content. Released state SHALL retain only unresolved generated-checkout and branch debt. Cleanup SHALL remove only clean ZPP-owned generated worktrees. Finalization SHALL remove a released record only after generated worktrees are gone and every retained branch is reconciled or explicitly abandoned.

#### Scenario: Preserve unresolved generated work
- **WHEN** a codespace is released, cleaned, given branch dispositions, and finalized
- **THEN** ZPP removes only state whose generated work has been safely resolved and retains every unresolved checkout or branch

### Requirement: Explicit reconciliation boundary
ZPP SHALL preserve generated project and governing-store branch metadata for the permanent codespace worktree-reconciliation skill. Locking, adding, opening, activation, execution, unlocking, cleanup, recovery, disposition recording, and finalization SHALL NOT merge isolated work automatically.

#### Scenario: Leave reconciliation explicit
- **WHEN** codespace lifecycle operations finish with isolated branches
- **THEN** their reconciliation metadata remains available until an explicitly invoked reconciliation workflow records a disposition

### Requirement: Bounded optional workset projections
An active codespace SHALL have zero or one ZPP-owned OpenSpec workset projection, created only when opening is requested. Its name SHALL be `zpp-<instance>-g<generation>`, where generation changes only when membership or effective paths change. Repeated opening of an unchanged effective view SHALL reuse the projection.

At each mutating codespace boundary, ZPP SHALL remove provably orphaned ZPP-owned projections absent from the durable active index without removing user-owned worksets, branches, or worktrees. Finalized history SHALL retain no complete historical projection, so durable storage grows only with active claims and unresolved generated work.

#### Scenario: Maintain a bounded opening projection
- **WHEN** an active codespace is opened, structurally changed, released, or found absent from the durable index
- **THEN** ZPP retains at most its current projection and removes only superseded or orphaned ZPP-owned projections

### Requirement: Cooperative agent claim guarding
The default profile SHALL provide a platform-neutral claim-guard trait that directs write-capable workflows to obtain or verify the complete claim automatically or prompt before acquisition according to effective workflow configuration. Claim exclusivity SHALL remain enforced by ZPP core even when the advisory trait is inactive or overridden.

Installed agent guards SHALL reject supported direct edit or write calls that explicitly target a checkout owned by another active codespace and SHALL identify that owner. Shell guarding SHALL verify association with the active codespace and current checkout without claiming to infer every path an arbitrary command may mutate. Manual editor actions, unrelated processes, unsupported tool paths, and cross-machine writes SHALL remain outside this guarantee.

#### Scenario: Reject a supported conflicting direct write
- **WHEN** a configured agent attempts a supported direct mutation against a checkout owned by another active codespace
- **THEN** the guard rejects the mutation using claim ownership rather than OpenSpec workset membership

Executable public examples for every requirement are maintained in `features/codespace_locking.feature` and `features/bootstrap_and_agents.feature`.
