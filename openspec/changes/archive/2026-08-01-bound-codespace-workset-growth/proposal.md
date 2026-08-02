## Why

The current codespace model conflates an OpenSpec workset with write ownership.
OpenSpec defines a workset as a personal local view of folders to open together;
it can contain multiple repositories and multiple OpenSpec roots, while each
normal OpenSpec command still resolves exactly one root. A workset therefore
cannot establish exclusive write authority or prevent simultaneous writes.

ZPP must separate optional editor composition from durable concurrency control.
It must also avoid retaining a new derived workset for every historical
combination of projects and stores.

## What Changes

- Define a codespace claim, rather than an OpenSpec workset, as the durable owner
  of the write targets reserved by one active codespace.
- Enforce claims between ZPP processes on the same machine. Cross-machine
  coordination is outside this change and remains governed by normal Git
  integration rather than a promised distributed lock.
- Treat an OpenSpec workset as an optional opening projection only, with zero or
  one ZPP-owned projection per active codespace. A workset SHALL NOT grant,
  transfer, or prove write ownership. Create the projection only when opening a
  codespace is requested.
- Discover writable targets portably from the active claim containing the
  current directory, an explicit workspace descriptor, or explicit paths, then
  deduplicate them by effective physical Git checkout. An agent or editor
  adapter MAY supply its current folder set when its native API exposes that
  information, but core locking SHALL NOT depend on an editor integration or
  infer ownership from an OpenSpec workset.
- Claim each complete writable project checkout. Resolve its OpenSpec authority
  according to OpenSpec root resolution and additionally claim the effective
  checkout of an external selected, pointed-to, or default standalone store.
  A repo-local OpenSpec root is already covered by its containing project
  checkout. Referenced stores remain read-only context unless independently
  selected as writable work.
- Acquire the complete requested set of write targets as one operation before
  permitting work. A partially acquired set SHALL NOT remain active.
- Arbitrate competing acquisitions so two concurrent ZPP processes cannot both
  successfully claim the same target after observing it as available.
- Add one platform-neutral claim-guard trait to the default profile. It directs
  every write-capable workflow to obtain or verify the current codespace claim
  before mutation, while profile configuration may select automatic acquisition
  or manual prompting.
- Keep claim exclusivity in ZPP core rather than in the advisory trait.
  Disabling or overriding the trait SHALL NOT allow two active ZPP claims to
  own the same physical checkout.
- Define installed agent enforcement as a cooperative guardrail around
  ZPP-managed work. A guard SHALL reject supported direct edit/write tool calls
  that explicitly target a checkout owned by another claim. Shell work SHALL be
  associated with the active codespace and current checkout, but ZPP SHALL NOT
  claim to infer every path an arbitrary shell command may mutate.
- Keep manual editor actions, unrelated processes, unsupported agent tool paths,
  and cross-machine writes outside the enforcement guarantee. This change SHALL
  NOT introduce OS sandboxing, filesystem permission isolation, or an editor
  extension solely to claim universal write prevention or discover open folders.
- Present the common guard through the trait instead of copying its policy into
  every skill. Update individual skills only where they encode conflicting
  workset ownership or directly govern codespace claim, worktree, release, or
  reconciliation behavior.
- Prevent two active codespace claims from owning the same effective physical
  write target. An isolated Git worktree or isolated store checkout is a
  distinct effective target and may be used to mitigate a conflict.
- Name every projection `zpp-<instance>-g<generation>`, where generation changes
  only when membership or effective paths change and never derives from the
  previous workset name.
- Preserve the full snapshot hash as immutable starting provenance in codespace
  metadata. File edits, new commits, and checkout movement SHALL NOT replace the
  claim, change its generation, or rewrite its starting snapshot.
- Make locking an already active identical effective view idempotently resolve
  to its existing codespace rather than creating another claim or projection.
- Keep conflict mitigation for overlapping but distinct views; do not collapse
  independent concurrent work merely because it begins from the same source
  commits.
- Reduce released state to outstanding generated-checkout and branch
  reconciliation debt instead of retaining complete historical workset views.
- Let the explicit reconciliation skill finalize a released record after it
  verifies every retained branch disposition, with `zpp codespace finalize ID`
  as the manual fallback. Finalization removes the record only after generated
  worktrees are gone and branches are reconciled or explicitly abandoned.
- At every mutating codespace boundary, automatically remove provably orphaned
  ZPP-owned workset projections absent from the durable active index without
  deleting worktrees, branches, or user-owned worksets.
- Use lifecycle invariants rather than an arbitrary numeric cap: storage grows
  with active claims plus unresolved generated work and optional active
  projections, not with every possible member combination.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codespace-locking`: Separate exclusive write-target claims from optional
  workset projections; bound projection cardinality, replacement identity,
  released reconciliation retention, and safe orphan disposal.

## Impact

- Affects codespace lock/add/unlock/cleanup/reconciliation behavior, write-target
  resolution, atomic claim acquisition, the durable codespace index, optional
  workset naming, recovery checks, the default profile trait set, installed agent
  guards, and codespace-specific workflow skills.
- Preserves the existing rule that dirty or unreconciled generated work is
  never discarded automatically.
- Does not impose a limit on legitimate concurrent codespaces or change shared
  OpenSpec store registration.

## Unresolved — Do Not Assume

None.
