# OpenSpec maintenance contract

Apply this contract before changing canonical specifications, affecting zmem, or deleting an archived change.

## Output order

Lead with a short decision summary:

1. removable exact paths;
2. paths waiting for ten-version age and their current counts;
3. canonical merges required;
4. zmem cancellations required;
5. unresolved owner decisions.

Place detailed evidence after the summary. Do not make the owner interpret the full audit to discover the next action.

## Preservation map

Classify each accepted archive item by what it represents:

| Item | Required authority |
| --- | --- |
| Current behavior or constraint | Canonical OpenSpec requirement |
| Current scenario without qualifying BDD coverage, or current serialization | Complete canonical OpenSpec scenario or clause |
| Current scenario with qualifying BDD coverage | Canonical target-form scenario plus its exact feature-owned executable behavior |
| Current owner boundary | Canonical OpenSpec requirement |
| Historical rationale | Traceable zmem decision or lesson |
| Fully superseded decision | Traceable zmem decision, followed by exact `CANCEL` |

The appropriate destination is sufficient. Do not require every proposal sentence, design explanation, task checkbox, requirement, and scenario in both stores. A stale task checkbox is evidence to inspect, not an independent blocker when code, canonical specs, or repository history proves its outcome.

Never use zmem as the only home of current normative behavior. Partial preservation, unresolved policy, contradictory destinations, and ambiguous ownership block removal.

## BDD-target preservation

An OpenSpec scenario may omit duplicated executable steps only when it retains an
exact target of this form:

```markdown
#### Scenario: BDD target — <scenario name>
- **WHEN** executable behavior is covered by `features/<capability>/<capability>.feature::<scenario name>`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
```

Verify the exact feature and scenario exist, share the capability owner, trace to
the requirement, use scenario-selected bindings that exercise the named behavior
through the public system, and pass relevant verification. A recorder, wording
assertion, shared capability-wide assertion, semantic guess, stale path, or failed
verification provides no coverage.

Preservation for covered behavior is the pair: canonical requirement and target,
plus the exact feature-owned executable scenario. Preserve a complete canonical
WHEN/THEN scenario whenever that pair cannot be proven. If either half of an
existing pair is stale or insufficient, mark consolidation and archive removal
blocked until the full scenario is restored or valid coverage is established.

## Same-behavior consolidation

Create this mapping when canonical requirements may overlap:

| Field | Required content |
| --- | --- |
| Sources | Exact capabilities, requirements, and scenarios |
| Behavior and owner | The behavior and owner boundary each source governs |
| Destination | One authoritative canonical capability and requirement |
| Preserved contract | Every mutually accepted current constraint and scenario |
| Superseded content | Clauses or scenarios current authority replaces |
| Conflict | Any unresolved semantic or ownership difference |
| Removal | Exact redundant requirement or capability path |

Merge only when behavior and owner match. Shared terminology is not duplication. Preserve the strongest mutually accepted current contract, not obsolete stronger wording. Expose an unresolved choice under `Unresolved — Do Not Assume` in the active workflow change.

## Ten-version age

For each superseded archive or spec item:

1. Identify its capability from the delta path.
2. Resolve the Git commit that archived its change.
3. Order later archive commits by Git history.
4. Count each later archived change once when its delta contains that capability.
5. Mark the item aged only when the count reaches ten.

For a multi-capability archive, every superseded item must satisfy its own capability count. The archive gate is the least-aged superseded item. Do not count arbitrary commits, project releases, filename dates, or later archives that omit the capability.

Do not apply this grace period to non-superseded redundant content whose current behavior or historical rationale is already preserved.

## zmem effects

When current authority proves a valid `DECISION` fully superseded:

1. Use `zmem-query-memory` to find it.
2. Inspect it with `zmem show` and copy its exact SHA and one-based annotation index.
3. Use `zmem-author-commits` to add `zmem(CANCEL)[sha, index]` to an authorized commit.
4. Validate the complete message with deep replay and inspect the resulting commit with `zmem show`.

Cancel immediately; do not wait for ten archive versions. Do not cancel a lesson, a partly valid decision, or an unresolved conflict. A partly valid decision may warrant deliberate `DECAY` after its exact target and surviving scope are established.

## Per-path audit record

Record each exact archived path with:

- affected capabilities;
- item-level canonical or zmem preservation destinations;
- exact BDD targets and scenario-selected verification when executable behavior is feature-owned;
- required canonical merges;
- superseded items and capability-version counts;
- required zmem effects;
- unresolved semantic or owner decisions;
- Git archive commit and recoverability;
- strict validation revision;
- outcome: `removable`, `waiting-age`, `merge-required`, `cancel-required`, or `blocked`;
- concise reason and exact next action.

## Mutation sequence

1. Complete the read-only summary, preservation map, consolidation map, age calculation, and zmem target resolution.
2. Reconcile canonical specifications through explicit current ZPP kernel authority
   and the exact installed `zpps-update-change`, `zpps-sync-specs`,
   `zpps-verify-change`, and `zpps-archive-change` adapters required by the action.
3. Apply authorized zmem effects through `zmem-author-commits` and deep validation.
4. Run strict OpenSpec validation and inspect the full diff.
5. Present only removable exact archive paths.
6. Obtain owner authorization naming each path.
7. Reconfirm the authorized set is unchanged and contained by the archive root.
8. Remove only the authorized paths, show the deletion diff, and rerun strict validation.
9. Use `zmem-author-commits` for an authorized deletion commit and inspect it with `zmem show`.

Canonical reconciliation, zmem effects, exact-path deletion, and commit creation are separate authorities. One never implies another.
