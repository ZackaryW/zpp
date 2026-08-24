## Context

See `proposal.md` for motivation. The hard-cut workflow family currently packages
five entries. `zpp-legacy-workflow` contains the complete generic ZPP 2 sequence,
while `zpp-auto` selects it for mixed, unsupported, maintenance-only, or unresolved
outcomes. The repository also has a distinct direct route for ungoverned
artifact-only maintenance. Because workflow behavior is delivered as installed skill
artifacts, entry identity and projection inventory are public product surfaces even
when routing prose has no honest executable observation.

## Goals / Non-Goals

**Goals:**

- Give the current generic workflow a truthful, discoverable identity.
- Separate generic product fallback, explicit legacy compatibility, direct
  ungoverned-artifact maintenance, and genuine non-workflow requests.
- Preserve complete sequencing in current playbooks and the existing kernel and
  component authority boundaries.
- Migrate installed owned inventories deterministically without adopting or deleting
  unowned destinations.

**Non-Goals:**

- Restore the removed monolithic `zpp-workflow` identity or any ZPP 1.x stage skill.
- Add heuristic classification code or claim that artifact wording is executable
  routing behavior.
- Change lifecycle stages, OpenSpec adapters, Bundler coordination, or trait hooks.
- Treat every unknown request as a ZPP product workflow.

## Decisions

### Add an explicit current generic identity

Package `zpp-generic-workflow` by moving the complete ordered generic sequence from
`zpp-legacy-workflow` without changing its stage behavior. This name is preferred
over restoring `zpp-workflow` because the hard cut deliberately retired that
monolithic identity and lifecycle migration already treats it as obsolete.

Alternative: keep the generic sequence under `zpp-legacy-workflow`. Rejected because
the name makes compatibility and current behavior indistinguishable and encourages
automatic triage to use legacy as a garbage-bin route.

### Make automatic fallback require a product workflow

`zpp-auto` will select the generic playbook only when the request is still a ZPP
product workflow but is mixed, maintenance-oriented, or otherwise unspecialized.
After bounded evidence inspection, a genuine non-match will return a no-handoff
triage result. It will not acquire a lease, mutate governed state, or invoke a
playbook merely because no specialized route matched.

The established direct route for ungoverned README/reference, repository-local
context/trait, or commit-metadata maintenance remains separate. Those requests match
an explicit maintenance route; they are not generic fallback or non-matches.

Alternative: send every non-match to the generic workflow for clarification.
Rejected because unrelated requests would enter product planning and make
classification failure look like product intent.

### Keep legacy as an explicit one-hop adapter

`zpp-legacy-workflow` will accept only an explicit invocation using the immediately
preceding consolidated/generic request shape and invoke `zpp-generic-workflow`
exactly once with the original request, roots, accepted owner input, and only supplied
authority. It will not copy stages, select continuation, translate ZPP 1.x
`zpp-flow-*` identities, or participate in automatic routing.

Alternative: remove legacy immediately. Rejected because an explicit compatibility
entry gives callers a bounded migration path while preventing it from influencing
new automatic decisions.

### Verify only observable installed behavior

Extend the established installed-inventory scenario and focused artifact matrices to
prove the generic and legacy entries are packaged and projected in deterministic
order. Keep routing classification and one-hop semantics normative in OpenSpec and
the skill contracts; do not fabricate a runtime router or assert arbitrary Markdown
phrases as behavior.

## Risks / Trade-offs

- [More installed entries can appear to add authority] → Describe generic as the
  complete playbook and legacy as a one-hop adapter with no lifecycle policy.
- [Non-match can be confused with unresolved product intent] → Require the request to
  be product-workflow-shaped before generic fallback; use bounded exploration once
  when repository evidence can resolve classification.
- [Owned installations omit the new entry] → Let existing initialization,
  synchronization, grouped workflow update, and reset consume the shared current
  inventory and preserve ownership-safe conflict behavior.
- [Compatibility becomes permanent] → Keep automatic routing away from legacy and
  retain removal as an explicit future breaking-release decision.

## Migration Plan

1. Establish RED inventory evidence for the new current entry.
2. Add `zpp-generic-workflow`, narrow `zpp-auto`, and reduce legacy to the adapter.
3. Update the deterministic packaged inventory and lifecycle expectations.
4. Synchronize the canonical workflow specification and run complete verification.

Rollback restores the five-entry hard-cut inventory, moves the generic sequence back
to `zpp-legacy-workflow`, and restores its former automatic fallback selection.
