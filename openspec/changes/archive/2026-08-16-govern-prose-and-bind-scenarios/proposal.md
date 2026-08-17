## Why

Prose and behavior have swapped places. The packaged workflow skill's own wording ships without any canonical requirement behind it, because the artifact-only maintenance route exempts it. Meanwhile the repository's scenarios verify wording instead of behavior: every step binds to a recorder that exercises nothing, and each capability's real assertions run as one undifferentiated block after every scenario in its root. Specifications should govern prose and scenarios should exercise the public system, and today neither holds.

## What Changes

- Exclude spec-governed packaged artifacts from artifact-only maintenance, so the packaged workflow skill, packaged trait documents, and canonical specifications reconcile their specifications before finalization.
- Reconcile the shipped monorepo behavior-ownership guidance into a canonical requirement.
- Require every scenario to bind to executable verification that exercises the described behavior through the public system. A step that records its own phrase or observes nothing does not satisfy that obligation.
- Require obligations expressible only as prose to live in canonical specifications rather than as scenarios, and prohibit verification that asserts literal wording already governed by a canonical requirement.
- State the binding rule in the packaged BDD guidance so every repository using ZPP receives it, not only this one.
- Apply the rule to this repository: remove wording assertions, replace recording-only bindings with verification that exercises the public system, and withdraw scenarios describing conduct no code observes.
- Repair the path comparisons that fail the established verification set on Windows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Constrains the artifact-only maintenance route so it cannot exempt spec-governed packaged artifacts, establishes monorepo behavior ownership, and requires scenarios to bind to executable public-system verification while routing prose obligations to specifications.

## Impact

- Packaged `zpp-workflow` instructions, the packaged `bdd` trait guidance, and the `consolidated-workflow-skill` canonical specification.
- This repository's `features/` roots and `features/support/contracts.py`, whose scenario inventory and assertions change substantially.
- Path comparisons in `features/support/contracts.py`, `tests/unit/test_agent_router_adapter.py`, and `tests/unit/test_openlease_adapter.py`.
- No CLI, runtime, or hook behavior changes.

## Unresolved — Do Not Assume

None.
