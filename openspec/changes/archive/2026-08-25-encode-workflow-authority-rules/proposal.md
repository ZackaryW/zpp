## Why

Workflow evidence currently permits weak BDD assertions, duplicates feature scenarios as OpenSpec trace scenarios, checkpoints active change artifacts, and always treats OpenSpec archive history as the terminal preservation mechanism. These rules blur executable authority, planning state, and durable memory.

## What Changes

- Reject BDD evidence based only on literal text matching, execution recording, or pure item counting without an observed behavioral relationship.
- Continue incremental source/test commits, but exclude the active OpenSpec change directory from every checkpoint; its artifacts become committable only after normal archive.
- Remove an OpenSpec scenario whenever an exact feature scenario owns that executable behavior; retain only requirement-level feature binding identity.
- Add a zmem-fold terminal route for changes whose complete durable information is a simple decision with no nested behavior, branching, serialization, or current normative contract: validate the zmem commit, remove the active change without creating an OpenSpec archive, commit the work and memory, and truthfully release coordination.
- Keep active change tasks updated throughout both normal-archive and zmem-fold routes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Changes BDD evidence quality, feature/OpenSpec authority separation, incremental checkpoint path selection, and terminal archive-versus-memory preservation.
- `openspec-maintenance-skill`: Removes target-form OpenSpec scenarios for BDD-owned behavior and recognizes valid zmem-fold provenance without treating a missing OpenSpec archive as loss.

## Impact

- Changes all complete playbooks, the workflow kernel, BDD shaping/specification formation, verification/finalization, single-change archive behavior, and zmem commit guidance.
- Changes component result vocabularies and exact workflow contract tests where new terminal results are introduced.
- Revises canonical OpenSpec authority and existing BDD-binding expectations.
- Does not suppress incremental implementation commits; it prevents active planning artifacts from entering those commits.
