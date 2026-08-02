## Context

The permanent clarification skill currently treats `proposal.md` as the only
planning artifact and blocks delta specs until post-green formation. The
packaged skills are the source for managed projections; the repository-local
`.codex` copy is an ignored development projection.

## Goals / Non-Goals

**Goals:**

- Restore OpenSpec's capability-specific delta-spec structure during
  clarification.
- Preserve the established BDD ownership of executable public examples.
- Keep post-green canonical promotion evidence-based.

**Non-Goals:**

- Change runtime CLI behavior or OpenSpec's artifact schemas.
- Put platform-specific policy into permanent workflow skills.
- Promote unresolved behavior into a delta spec.

## Decisions

### Treat the selected OpenSpec schema as artifact authority

ZPP will stop imposing a universal proposal-only artifact shape. Clarification
will obtain current artifact status and instructions from OpenSpec and maintain
the proposal plus every capability delta required by the proposal.

Alternative: add a ZPP-specific multi-file schema. Rejected because OpenSpec
already owns artifact layout and validation.

### Separate unresolved overview from settled capability contracts

`proposal.md` will retain change-wide overview and unresolved owner decisions.
Settled behavior will be written into the corresponding capability delta
immediately after each clarification response.

Alternative: copy the same details into both artifacts. Rejected because it
recreates the duplication this change removes.

### Preserve downstream ownership transitions

Feature shaping will read both artifact classes and remove only examples that
Gherkin supersedes. Specification formation will update and sync the existing
deltas after green verification rather than constructing new deltas from a
monolithic proposal.

Alternative: leave downstream skills unchanged. Rejected because their current
wording would postpone or recreate specs and contradict clarification.

## Risks / Trade-offs

- [More artifacts must stay coherent during clarification] → Reconcile the
  complete declared capability set after every settled response.
- [Unresolved behavior could leak into normative deltas] → Keep unresolved
  branches only in the proposal until the owner settles them.
- [Installed development skills could drift from packaged sources] → Update
  the packaged skills first, refresh the `.codex` projection, and validate both.
