## Context

ZPP currently resolves each family against one base context, then backfills facets from retained evidence-selected flavors after selection. That makes the result available to a later invocation but prevents a detected value such as `language = "typescript"` from activating another family during the current invocation. Stored provenance is key-wide, so a changed fingerprint invalidates a complete list rather than one evidence-derived member.

Traits remain one-family TOML documents with complete bodies. Workflow stages and their outcomes remain owned by the consolidated skill and the acting agent.

## Goals / Non-Goals

**Goals:**

- Enrich the shared descriptive context from successful trait evidence before final family selection.
- Let all families match the enriched context during the same agent invocation.
- Extend list-valued descriptive context as a deterministic ordered set with member-level provenance and invalidation.
- Perform enrichment within the existing resolver called by the established session-start hooks.
- Keep explicit workflow runtime controls protected from repository authoring, trait derivation, durable export, and stored descriptive backfill.
- Let the agent declare conditional stages complete or not applicable while the workflow skill enforces the evidence gate.
- Prevent newer prompts or assistant recommendations from silently contradicting or replacing older accepted change input.

**Non-Goals:**

- Adding workflow metadata to trait TOML.
- Adding a separate invocation command, resolution skill, prompt-by-prompt resolution hook, or hidden session database.
- Inferring a workflow stage from files, prompts, traits, or stored descriptive context.
- Recursively deriving context from flavors selected only because another facet was derived.
- Automatically writing discovered values to `.zpp/zpp.toml`.

## Decisions

### Use one bounded enrichment pass before final selection

Resolution first builds the base context using stored → repository → explicit invocation precedence and collects workspace evidence once. It then forms evidence-backed enrichment candidates in deterministic effective-family and flavor order. `first-win` contributes its first compatible successful evidence fallback only when it has no direct winner; `all` and `extend` contribute every compatible successful evidence candidate. Successful branches contribute declared flavor facets and typed evidence facts.

The enriched context is then used for one final selection pass across every family. A flavor selected only from enriched facets does not contribute another round of derived facets. This gives same-invocation specialization without a recursive fixed point or selection loop.

Alternatives rejected:

- Post-selection backfill alone defers cross-family specialization to a later invocation.
- Recursive resolution can make selection dependent on convergence order and retain stale intermediate derivations.
- A separate `[trait.derive]` table duplicates the facet values that evidence already identifies.

### Treat list-valued descriptive context as an ordered set

Established authored members remain first. New evidence-derived members append in deterministic enrichment order and exact duplicates are ignored. An explicit invocation value replaces lower-precedence values and is not expanded by evidence. Repository list values and evidence-owned scalar or list values may receive new evidence members; an authoritative repository scalar remains exact.

Stored context records provenance and evidence keys per value. When evidence changes, only members supported by drifted evidence are removed. A key is removed only when no members remain. Version-1 stored context remains readable and is upgraded when re-encoded.

### Keep workflow controls outside descriptive derivation

The current stage is an explicit runtime input. Repository context, stored descriptive context, `when` evidence, and trait backfill cannot author reserved workflow-control keys. Runtime controls are usable as facet match inputs for the current invocation but are not included in exportable descriptive context. The consolidated skill remains responsible for declaring each visible stage action and enforcing its outcome.

### Extend the existing resolver and hook boundary

`zpp resolve` remains the only public resolution operation. It performs evidence enrichment and final family selection atomically, returns prompt-ready complete bodies by default, and exposes the enriched target-bound context through the existing structured diagnostic and `ZPP_CONTEXT` session-integration contract. It does not create an invocation subcommand, require a resolver skill, or maintain a hidden session database.

The existing agent-native session-start hooks continue calling `zpp resolve --agent <agent> .`. They receive the final complete bodies from the enriched resolution without changing to `UserPromptSubmit`. Invocation describes when the established hook runs; it is not a second CLI operation or agent-launching responsibility.

### Reconcile the complete agreement history before convergence

At every clarification update, classify the new input as an explicit confirmation, correction, recommendation, exploration, or deferral. Reconcile it against canonical specifications, every older accepted owner statement in the current change, the proposal, every capability delta, and any already-shaped downstream contract. A newer statement does not silently replace older input merely because it is newer.

Only explicit owner confirmation can promote a recommendation or unresolved branch into normative deltas. A contradiction remains visible in `Unresolved — Do Not Assume`, blocks convergence, and invalidates every downstream gate formed from the superseded contract. Automatic end-to-end delegation authorizes continuation across satisfied gates but does not answer an unresolved product decision.

### Keep repository export explicit

The resolver returns the enriched context and provenance. Promoting suitable descriptive values into `.zpp/zpp.toml` remains an explicit exact-document mutation through OpenLease. Workflow controls and machine-local availability facts are not automatically exportable. Promotion changes a detected session fact into an owner-authored repository declaration.

## Risks / Trade-offs

- **More evidence is evaluated before final selection** → collect each predicate once and reuse its result and fingerprint.
- **A detected member may become stale** → retain member-level evidence provenance and remove only drifted members on restoration.
- **A new prompt can appear to settle only one side of an older contradiction** → review the complete accepted-input inventory before updating any normative delta.
- **A repository may contain several ecosystems intentionally** → retain distinct list members rather than forcing one detected language.

## Migration Plan

1. Accept version-1 `ZPP_CONTEXT` values and normalize them into member-level provenance.
2. Emit the new deterministic stored-context representation on the next successful resolution.
3. Preserve all existing session-start hook events and command ownership while the resolver implementation changes beneath their public contract.
4. Preserve all existing trait TOML and repository context documents unchanged.

Rollback restores the previous resolver. Repository trait documents and hook projections require no rollback under the currently confirmed scope.

## Open Questions

None.

## Replacement Assessment

The built `zpp-2.0.0` wheel is technically ready to replace the active workflow:
its isolated install resolves traits successfully, contains one consolidated
workflow skill, packages only SessionStart resolution hooks, and uses the pinned
Agent Router home-location behavior. No implementation or packaging blocker
remains.

The inspected live environment still runs ZPP 1.0.2, retains the seven legacy
`zpp-flow-*` skills, and does not yet contain `zpp-workflow`. Replacement therefore
requires an explicit deployment of the 2.0.0 wheel, projection of the new workflow
skill and hook through Agent Router, and a new agent session so skill discovery is
refreshed. Finalization intentionally did not mutate those active destinations.
