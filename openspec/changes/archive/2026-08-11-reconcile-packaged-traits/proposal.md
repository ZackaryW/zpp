## Why

The packaged collection still contains unconditional OpenLease coordination and finalization policy that belongs to component and workflow authorities, not repository environment traits. It also retains an ambiguously named BDD execution family and a tooling flavor that duplicates the dedicated zmem skills.

## What Changes

- Remove `lease-complete-affected-set`, `lease-conflict-policy`, and `reconciliation-gate` from the packaged trait collection.
- Keep OpenLease lease/conflict handling with OpenLease and keep final reconciliation requirements in the consolidated workflow skill.
- **BREAKING** Rename the packaged `bdd-workflow` family to `bdd-execution`; ZPP does not provide a compatibility alias because 2.0 does not retain legacy trait families.
- Preserve the BDD execution family's existing `manual`, `disabled`, `complete`, `targeted`, and targeted-default behavior under the clearer name.
- Declare `zero-assumptions` as explicitly `always-run` so its universal activation is intentional rather than an empty-facet side effect.
- Remove the `zmem` flavor from `tooling`; dedicated zmem skills remain the authority for recall and commit-memory behavior.
- Retain `bdd`, `bdd-structure`, `tdd`, `build`, `dependencies`, and the `rg`/`jq` tooling flavors unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Reconciles the standard packaged behavior inventory so component-owned lease/conflict policy and skill-owned reconciliation are no longer duplicated as traits, while preserving the clarified BDD execution and universal advisory families.

## Impact

- Affects packaged TOML assets, packaged-family tests, BDD collection verification, README examples, and the consolidated workflow skill canonical inventory.
- Repository, space, or plugin collections that independently define the removed family names remain valid user-owned trait documents; only ZPP's packaged defaults change.
- Existing contexts that name packaged `bdd-workflow` must use `bdd-execution` after this breaking collection cleanup.

## Unresolved — Do Not Assume

None. The owner accepted the complete collection review and the exact reconciliation above.
