## Context

All packaged TOML documents are global fallback contributions. A one-flavor document with no facets or evidence directly matches every resolution under automatic activation, so the lease, conflict, reconciliation, and zero-assumption families currently behave as universal policy. Three of those universal families describe component or workflow operations rather than repository environment behavior. The recently restored native hook injects all common packaged matches automatically, making this boundary especially important.

## Goals / Non-Goals

**Goals:**

- Keep the packaged collection small, precise, and advisory.
- Remove duplicated OpenLease and workflow authority from automatic context.
- Make the universal zero-assumption behavior explicit.
- Give BDD execution policy a name that cannot be mistaken for the ZPP workflow.
- Keep tool guidance with tools while leaving zmem policy to its dedicated skills.

**Non-Goals:**

- Preventing user-owned collections from defining lease or reconciliation families.
- Changing selection, activation, filtering, or composition algorithms.
- Adding compatibility aliases or migration code for packaged family names.
- Expanding the currently accepted language flavors for build, BDD, or TDD.

## Decisions

### Remove operational coordination from packaged traits

Delete the three packaged lease/reconciliation documents. OpenLease exposes conflicts and owns coordination; the consolidated workflow skill already requires final successor reconciliation. Keeping a passive globally injected paraphrase creates ambiguous authority and stale guard claims.

### Rename the BDD mode family without an alias

Move `bdd-workflow.toml` to `bdd-execution.toml` without changing its metadata, flavor order, or bodies. Its facet-controlled first-win behavior is correct, but its former name implies a workflow definition. An alias would emit duplicate bodies and contradict the no-legacy-compatibility contract.

### Make universal policy explicit

Set `[meta].activation = "always-run"` for `zero-assumptions`. Its one flavor remains subject to first-win selection, but its universal role no longer depends on vacuous facet matching.

### Remove zmem from generic tooling

Retain the evidence-backed `rg` and `jq` flavors. Remove `zmem` because its body delegates to dedicated skills that already own when and how temporal memory is used; injecting it whenever the executable exists is redundant.

## Risks / Trade-offs

- **[Existing users request `bdd-workflow`]** → Document the direct `bdd-execution` replacement; do not inject duplicate compatibility content.
- **[Lease guidance disappears from common prompts]** → Preserve actual authority in OpenLease and the workflow skill rather than passive global prose.
- **[Universal activation changes implementation path]** → Existing selected output remains identical for `zero-assumptions`; tests prove only the metadata/decision path changes.

## Migration Plan

Update feature expectations first, then mutate only the packaged documents and collection inventory tests. Verify default and filtered resolution, wheel contents, canonical OpenSpec, and the complete behavior suite. Rollback restores the deleted files and prior family name.

## Open Questions

None.
