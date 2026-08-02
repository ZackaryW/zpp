## MODIFIED Requirements

### Requirement: Explicit on-demand view claims
ZPP SHALL create a durable machine-local codespace only from explicit writable
paths, an explicit workspace descriptor containing writable paths, or an
existing active codespace whose writable member contains the current checkout.
Explicit read-only paths MAY supplement an explicit writable target set. A
current directory contained only by a read-only member SHALL NOT
implicitly select a codespace; the user SHALL supply its identity or activate
its environment. OpenSpec worksets SHALL NOT establish, transfer, or prove write
ownership, and core locking SHALL NOT depend on editor folder discovery.

The exclusive claim SHALL cover each complete committed writable project
checkout and the effective checkout of every external writable OpenSpec store
selected by that project. A repo-local OpenSpec root SHALL be covered by its
containing writable project checkout, reference-only stores SHALL remain
unclaimed, and unclassified stores or writable repositories without a committed
`HEAD` SHALL cause the complete request to fail without partial state.

An explicitly selected read-only repository SHALL have a committed `HEAD` and
SHALL be retained separately as a non-owning member of the codespace view. Only
the explicitly selected repository SHALL be retained; ZPP SHALL NOT expand its
related OpenSpec stores into further view members. A read-only member SHALL NOT
enter the exclusive claim, expand the writable OpenSpec closure, conflict with
another claim, or cause ZPP to create an isolated worktree, and the same
physical read-only repository MAY participate in multiple codespaces.

#### Scenario: Claim a resolvable target set
- **WHEN** a user locks an explicit committed writable target set whose OpenSpec authority can be classified
- **THEN** ZPP atomically claims its complete writable closure without creating isolation, a workset projection, or an editor session

#### Scenario: Retain explicit read-only context
- **WHEN** a user locks writable repositories and supplies a repository through `--read-only`
- **THEN** ZPP records one codespace view containing both sets while claiming only the writable closure

#### Scenario: Do not mitigate a read-only overlap
- **WHEN** a selected read-only repository is already writable under another active codespace claim
- **THEN** ZPP retains the repository as non-owning context without reporting a writable conflict or creating a worktree

#### Scenario: Reject an uncommitted read-only repository
- **WHEN** a selected read-only repository has no committed `HEAD`
- **THEN** ZPP rejects the complete request without changing codespace state

#### Scenario: Retain only explicit read-only context
- **WHEN** an explicitly selected read-only repository resolves related external OpenSpec stores
- **THEN** ZPP retains only that repository unless those stores are independently selected as read-only paths

#### Scenario: Require explicit selection from shared read-only context
- **WHEN** the current directory belongs only to a read-only member that can participate in multiple codespaces
- **THEN** ZPP requires an explicit codespace identity or activated environment rather than inferring one

### Requirement: Separate snapshot, checkout, and instance identity
ZPP SHALL use effective physical checkout identity for exclusive active
ownership and SHALL record every member's full commit hash at acquisition as
immutable provenance for that codespace identity. File changes, new commits,
and checkout movement SHALL be reported as current state without automatically
replacing the codespace, changing its structural generation, or rewriting its
recorded snapshot.

An exact active effective shape SHALL resolve idempotently to its existing
identity. A successful explicit codespace edit SHALL calculate a successor
identity and snapshot from the resulting member roles, effective paths, and
full commits observed at the edit boundary, and SHALL atomically replace the
superseded active identity. An edit whose resulting shape is unchanged SHALL be
a no-op without confirmation or identity replacement. Independently isolated
physical checkouts MAY form a distinct identity even when they begin from the
same source commits.

#### Scenario: Retain an active identity across commit movement
- **WHEN** a member checkout changes after acquisition and the same effective shape is inspected or locked again
- **THEN** ZPP retains the existing identity and recorded snapshot while reporting current checkout state separately

#### Scenario: Recalculate identity after an explicit shape edit
- **WHEN** a user successfully edits the writable or read-only membership of an active codespace
- **THEN** ZPP atomically replaces it with the successor identity derived from the resulting shape and leaves no superseded active view

#### Scenario: Leave an unchanged edit as a no-op
- **WHEN** every requested edit operation produces the existing effective shape
- **THEN** ZPP retains the existing identity without requesting replacement confirmations

### Requirement: Atomic codespace lifecycle
ZPP SHALL expose lock, edit, list, status, optional open, activate, exec, unlock,
cleanup, disposition, recovery, and finalize operations. Editing SHALL replace
the complete codespace shape and its identity as one atomic operation; failure
or declined mitigation SHALL leave its original identity, writable claim, and
optional projection unchanged.

`zpp codespace edit [ID]` SHALL accept repeatable `--add`,
`--add-read-only`, `--remove`, `--promote`, and `--demote` path operations,
plus `--yes`/`-y`. ZPP SHALL remove the narrower `zpp codespace add` command.
Contradictory operations against the same physical checkout SHALL fail during
preflight without changing state.

Before an interactive edit replaces an existing lock, ZPP SHALL separately
confirm the complete successor shape and the release of the superseded lock.
Explicit `--yes` or `-y` authority SHALL preauthorize both confirmations. ZPP
SHALL complete successor validation and conflict planning before mutation and
SHALL transfer ownership as one atomic replacement; it SHALL NOT expose an
unlocked interval by releasing the existing claim before attempting its
successor.

Activation and wrapped execution SHALL use the codespace's private OpenSpec
registry. Unlock and forced recovery SHALL release write ownership and remove
only its ZPP-owned projection while preserving generated worktrees and content.
Released state SHALL retain only unresolved generated-checkout and branch debt.
Cleanup SHALL remove only clean ZPP-owned generated worktrees. Finalization
SHALL remove a released record only after generated worktrees are gone and every
retained branch is reconciled or explicitly abandoned.

Generated members retained by the successor SHALL transfer to it. Removing a
generated member SHALL preserve its worktree and branch as reconciliation debt
under the superseded identity. Demoting a generated writable member SHALL place
its canonical checkout in the successor as read-only context while preserving
the generated worktree and branch as superseded reconciliation debt. No edit
SHALL delete generated content.

#### Scenario: Replace a codespace shape atomically
- **WHEN** a requested edit changes writable or read-only membership and every required claim transition succeeds
- **THEN** ZPP exposes only the successor identity and complete resulting shape

#### Scenario: Preserve the original shape after edit failure
- **WHEN** any validation, ownership acquisition, mitigation, or persistence step of a codespace edit fails
- **THEN** ZPP retains the original identity, complete shape, claim, and optional projection

#### Scenario: Confirm replacement of an existing lock twice
- **WHEN** an interactive codespace edit targets an existing lock without `--yes` or `-y`
- **THEN** ZPP confirms both the successor shape and superseded-lock release before atomically replacing either

#### Scenario: Decline either edit confirmation
- **WHEN** a user declines either confirmation for an interactive codespace edit
- **THEN** ZPP leaves the existing identity, claim, shape, and optional projection unchanged

#### Scenario: Reject contradictory edit operations
- **WHEN** one edit assigns incompatible operations to the same physical checkout
- **THEN** ZPP rejects the request before confirmation or mutation

#### Scenario: Preserve generated work removed from the successor
- **WHEN** an edit removes or demotes a generated writable member
- **THEN** ZPP retains its worktree and branch as reconciliation debt under the superseded identity without deleting content

#### Scenario: Preserve unresolved generated work
- **WHEN** a codespace is released, cleaned, given branch dispositions, and finalized
- **THEN** ZPP removes only state whose generated work has been safely resolved and retains every unresolved checkout or branch

### Requirement: Explicit reconciliation boundary
ZPP SHALL preserve generated project and governing-store branch metadata for
the permanent codespace worktree-reconciliation skill. Locking, editing,
opening, activation, execution, unlocking, cleanup, recovery, disposition
recording, and finalization SHALL NOT merge isolated work automatically.

#### Scenario: Leave reconciliation explicit
- **WHEN** codespace lifecycle operations finish with isolated branches
- **THEN** their reconciliation metadata remains available until an explicitly invoked reconciliation workflow records a disposition

### Requirement: Bounded optional workset projections
An active codespace SHALL have zero or one ZPP-owned OpenSpec workset projection,
created only when opening is requested. The projection SHALL contain its
writable effective checkouts and its retained read-only repository paths. Its
name SHALL be `zpp-<instance>-g<generation>`, where generation changes only when
view membership or effective paths change. Repeated opening of an unchanged
effective view SHALL reuse the projection.

At each mutating codespace boundary, ZPP SHALL remove provably orphaned
ZPP-owned projections absent from the durable active index without removing
user-owned worksets, branches, or worktrees. Finalized history SHALL retain no
complete historical projection, so durable storage grows only with active
codespaces and unresolved generated work.

#### Scenario: Maintain a bounded opening projection
- **WHEN** an active codespace containing writable and read-only members is opened, structurally changed, released, or found absent from the durable index
- **THEN** ZPP projects its complete view, retains at most its current projection, and removes only superseded or orphaned ZPP-owned projections

### Requirement: Cooperative agent claim guarding
The default profile SHALL provide a platform-neutral claim-guard trait that
directs write-capable workflows to obtain or verify the complete writable claim
automatically or prompt before acquisition according to effective workflow
configuration. Claim exclusivity SHALL remain enforced by ZPP core even when
the advisory trait is inactive or overridden.

Installed agent guards SHALL reject supported direct edit or write calls that
explicitly target either a checkout owned by another active codespace or a
read-only member of the associated codespace, and SHALL identify the reason for
the rejection. Shell guarding SHALL verify association with the active
codespace and current checkout without claiming to infer every path an arbitrary
command may mutate. Manual editor actions, unrelated processes, unsupported tool
paths, and cross-machine writes SHALL remain outside this guarantee.

#### Scenario: Reject a supported conflicting direct write
- **WHEN** a configured agent attempts a supported direct mutation against a checkout owned by another active codespace
- **THEN** the guard rejects the mutation using claim ownership rather than OpenSpec workset membership

#### Scenario: Reject a supported write to associated read-only context
- **WHEN** a configured agent associated with a codespace attempts a supported direct mutation inside one of that codespace's read-only members
- **THEN** the guard rejects the mutation because that member is non-writable in the codespace view

## ADDED Requirements

### Requirement: Observable access roles
ZPP SHALL include every writable and read-only member in codespace status and
SHALL identify each member's effective access role. Read-only members SHALL NOT
be reported as claimed, generated, or pending reconciliation merely because
they belong to the view.

#### Scenario: Inspect a mixed-access codespace
- **WHEN** a user requests status for a codespace containing writable and read-only members
- **THEN** ZPP reports the complete view and distinguishes the access role of every member
