## Why

ZPP already combines invocation, repository, stored, and evidence-derived facets into a context dictionary, but evidence-derived facets are currently available only after family selection. Traits therefore cannot reliably specialize complete behavior bodies against facts discovered during the same resolution.

Stage applicability is not trait metadata. The agent must declare the stage outcome and the consolidated workflow skill must enforce its gate; traits should only match the current context and supply the repository-specific behavior rules used while making that decision.

## What Changes

- Treat the resolution context as a dynamic key/value match store. Existing `[trait.facet]` constraints may reference current descriptive context and protected runtime values without introducing a new trait schema table.
- Separate ordinary descriptive context from protected workflow runtime controls. Traits may read protected values such as the current stage for matching, but trait documents, repository context, evidence backfill, and stored context cannot author, overwrite, or restore those controls.
- Enrich missing descriptive context from successful `when` evidence before final family selection so every family can use the derived values in the same invocation. Do not recursively derive from facet-only matches.
- Treat list-valued descriptive fields as ordered unique sets: preserve established order, append distinct evidence-derived values deterministically, and track provenance and evidence fingerprints per value so invalidation removes only the affected derivation. Explicit invocation overrides remain authoritative.
- Extend the existing `zpp resolve` operation to perform enrichment and return the updated context; do not add an invocation command or resolution skill. Existing session-start hooks continue to call `resolve`, and no `UserPromptSubmit` resolution hook is introduced.
- Make the agent declare a conditional stage as `completed` or `skipped: not applicable`, with the consolidated workflow skill independently enforcing the stage's evidence gate. Trait matching or body wording cannot declare, authorize, or persist that outcome, and failed work cannot be relabeled as a skip.
- Keep `clarify` and `finalize` mandatory while allowing the five middle stages to be skipped only when their workflow-owned not-applicable gates are proven.
- Require clarification to reconcile every newer prompt, correction, recommendation, and apparent agreement against the complete older request and current change contract before changing normative deltas. Recommendations and exploratory language remain unresolved until the owner explicitly confirms them; contradictions reopen clarification and invalidate downstream gates.
- Preserve complete `content.body` output and the single consolidated workflow skill. Do not add `[trait.workflow]`, `skip_eligible`, a skip policy, a `workflow` trait family, or a packaged workflow trait.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `trait-resolution`: Generalize the context dictionary's matching contract, protect runtime control provenance and persistence, and preserve deterministic matching and backfill across repeated resolutions.
- `consolidated-workflow-skill`: Define agreement reconciliation and agent-declared, workflow-enforced stage outcomes without transferring applicability or completion authority to traits.

## Impact

The context model, session serialization boundary, invocation validation, existing resolver lifecycle, packaged workflow skill, behavior contracts, and documentation change. Existing trait TOML and hook events remain valid: `[trait.facet]`, `[[trait.when]]`, and `[trait.content]` retain their current roles, and no trait document receives workflow-control authority.

## Unresolved — Do Not Assume

None. The owner confirmed that invocation is a lifecycle concept rather than a new command: existing session-start hooks continue calling `zpp resolve`, the resolver performs same-resolution enrichment and returns updated `ZPP_CONTEXT` through its existing session-integration contract, no hidden session database is introduced, and repository export remains explicit.
