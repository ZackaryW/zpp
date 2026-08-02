## Purpose

Defines on-demand conflict gating for concurrent OpenSpec working views while preserving canonical checkouts when isolation is unnecessary.

## ADDED Requirements

### Requirement: Explicit on-demand view claims
ZPP SHALL create a durable codespace claim only from an explicit view, an existing claim containing the current checkout, or an unambiguous applicable OpenSpec workset. The claim SHALL include committed project checkouts and their complete governing-store closure, leave reference-only stores shared, reject unclassified stores or repositories without a committed `HEAD`, and project the resolved effective paths into a distinct ZPP-owned OpenSpec workset.

An uncontested claim SHALL use canonical checkouts without creating a worktree or opening an editor or agent.

#### Scenario: Claim a resolvable working view
- **WHEN** a user locks a resolvable committed working view
- **THEN** ZPP claims its complete writable closure without unnecessary isolation or opening

### Requirement: Separate snapshot, checkout, and instance identity
ZPP SHALL preserve every member commit hash in OpenSpec workset order, including duplicates, as the snapshot identity and SHALL report dirty state separately. Physical checkout identity SHALL govern exclusive active ownership even when a checkout advances to another commit. Each codespace SHALL also have a distinct instance identity so multiple isolated views MAY begin from the same snapshot.

#### Scenario: Detect overlap independently of commit movement
- **WHEN** a proposed view overlaps an actively claimed physical checkout
- **THEN** ZPP reports the complete overlapping writable closure regardless of matching or changed commit snapshots

### Requirement: Confirmed worktree mitigation
ZPP SHALL create isolation only after the user confirms a reported conflict. It SHALL retain uncontested canonical checkouts and create distinct sibling Git worktrees for the conflicting project and governing-store closure from each member's snapshotted commit without copying uncommitted content.

ZPP SHALL reject pre-existing target paths or branches without overwrite, register the effective paths as another owned OpenSpec workset, preserve original logical store IDs in a private registry, leave shared global store registration unchanged, and keep opening the prepared view optional.

#### Scenario: Mitigate a conflicting closure
- **WHEN** a user confirms mitigation for a conflicting working view
- **THEN** ZPP prepares an isolated effective view without changing the existing open workspace or shared OpenSpec registry

### Requirement: Atomic codespace lifecycle
ZPP SHALL expose lock, add, list, status, optional open, activate, exec, unlock, and cleanup operations. Adding paths SHALL replace the owned OpenSpec workset and transfer its claim atomically; failure or declined mitigation SHALL leave the original claim and workset unchanged.

Activation and wrapped execution SHALL use the codespace's private OpenSpec registry. Unlock and forced recovery SHALL release durable claims and remove only ZPP-owned workset registration while preserving worktrees and their contents. Cleanup SHALL remove only clean ZPP-owned generated worktrees and SHALL preserve dirty, canonical, and user-owned work.

#### Scenario: Maintain a codespace without losing work
- **WHEN** a user extends, inspects, uses, releases, recovers, or cleans a codespace
- **THEN** ZPP applies the requested lifecycle transition atomically within its ownership boundary

### Requirement: Explicit reconciliation boundary
ZPP SHALL preserve generated project and governing-store branch metadata for the permanent codespace worktree-reconciliation skill. Locking, adding, opening, activation, execution, unlocking, cleanup, and recovery SHALL NOT merge isolated work automatically.

#### Scenario: Leave reconciliation explicit
- **WHEN** codespace lifecycle operations finish with isolated branches
- **THEN** their reconciliation metadata remains available without any automatic merge

Executable public examples for every requirement are maintained in `features/codespace_locking.feature`.
