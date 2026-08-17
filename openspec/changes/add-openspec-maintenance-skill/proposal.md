## Why

OpenSpec archives preserve useful provenance, but indefinite growth makes stale deltas easier to mistake for current authority and makes duplicated canonical requirements more likely to contradict one another. ZPP needs a conservative maintenance guide that can identify safe consolidation and removal candidates without turning archive cleanup into an automatic destructive action.

## What Changes

- Package a new manually invoked `zpp-maintain-openspec` companion skill.
- Require the skill to audit canonical specifications and archived changes against current repository evidence and valid zmem before proposing consolidation or deletion.
- Require an explicit evidence table and exact-path maintenance plan before mutation.
- Permit canonical consolidation only when accepted requirements and scenarios remain represented without invented policy.
- Permit archived-change deletion only after canonical coverage, Git recoverability, and explicit owner authorization for the exact paths are established.
- Keep active changes, unresolved contradictions, ambiguous ownership, partial synchronization, and unique archive content out of automatic removal.
- Reuse the existing dynamic companion discovery and projection behavior; add no ZPP command, loader, or OpenSpec skill bootstrap.

## Capabilities

### New Capabilities

- `openspec-maintenance-skill`: Defines the packaged manual guidance and safety contract for auditing, consolidating, and selectively removing legacy OpenSpec artifacts.

### Modified Capabilities

None.

## Impact

- Adds one packaged companion skill under `src/zpp/artifacts/skills/companion/`, including interface metadata and a focused maintenance reference.
- Extends the expected packaged companion inventory exercised by unit tests; existing role discovery and lifecycle projection require no implementation change.
- Adds one canonical OpenSpec capability after synchronization.
- Introduces no dependency, public command, automatic hook, local OpenSpec skill initialization, or repository deletion as part of this change.
