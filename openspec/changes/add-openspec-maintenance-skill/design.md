## Context

ZPP already discovers every valid directory in the packaged `companion` role and projects those skills during supported-agent lifecycle operations. OpenSpec archives currently remain in Git indefinitely, while canonical specifications are the current authority. Archive cleanup is therefore primarily a semantic and destructive-maintenance problem: filename age and Git recoverability cannot prove that a delta is fully represented or that two requirements mean the same thing.

The repository's workflow contract also treats packaged skill instructions and canonical specifications as governed artifacts. The new skill must remain a manually invoked companion operation and must not acquire workflow-stage, OpenSpec-operation, commit, or deletion authority of its own.

## Goals / Non-Goals

**Goals:**

- Provide a repeatable audit that maps every candidate archived delta to current canonical requirements and scenarios.
- Expose contradictions, unique content, partial synchronization, and ownership ambiguity before mutation.
- Define a conservative consolidation contract that preserves accepted behavior and does not invent product policy.
- Require exact-path owner authorization and Git recoverability before removing archived changes.
- Reuse installed ZPP, OpenSpec, zmem, Git, and repository validation boundaries.

**Non-Goals:**

- Delete any archive as part of adding this skill.
- Treat archives as current specification authority or delete active changes.
- Add a ZPP command, hook, loader, maintenance script, dependency, or automatic cleanup schedule.
- Initialize, generate, install, project, repair, or substitute OpenSpec operation skills in a target repository.
- Consolidate distinct accepted requirements merely to reduce file count.

## Decisions

### Package a companion skill with a focused maintenance reference

Create `zpp-maintain-openspec` under the discovered companion role with `SKILL.md`, `agents/openai.yaml`, and `references/maintenance-contract.md`. Keep the required procedure in `SKILL.md`; place the detailed audit fields, eligibility matrix, and consolidation mapping in the reference.

This reuses role discovery instead of adding a manifest or loader branch. A standalone script was considered, but rejected: semantic equivalence, accepted-policy preservation, and contradiction resolution require repository-specific judgment. Existing `rg`, `jq`, Git, OpenSpec validation, and exact installed skills already cover the deterministic mechanics.

### Separate audit authority from mutation authority

The skill always begins read-only and emits an explicit candidate table. It may recommend canonical edits or archive removal, but a recommendation is not authority. Canonical edits run only through an explicitly invoked `zpp-workflow` change, and deletion additionally requires owner authorization naming each exact archive path.

This prevents a broad request such as “clean up OpenSpec” from silently authorizing recursive deletion. Automatic workflow progression may carry ordinary checkpoint commits for an accepted change, but does not answer contradictions or widen a deletion target.

### Make semantic coverage the removal gate

An archived change is eligible only when every delta requirement and scenario maps to current canonical authority, no unique accepted content or unresolved task state remains, contradictions are resolved by the owner, and Git can recover the exact path. Git recoverability is necessary provenance evidence, not proof of semantic safety.

Candidates with active status, partial synchronization, ambiguous ownership, unique content, unresolved contradictions, or absent Git provenance remain blocked and retained.

### Consolidate through explicit before/after mappings

Before editing canonical specifications, record the source requirements and scenarios, destination requirement, preserved behavior, conflict resolution, and expected removals. Consolidation may merge genuine duplication or clarify ownership, but must preserve all accepted constraints and scenarios and must not silently weaken normative language.

Use the installed `zmem-query-memory` skill for temporal evidence, while treating current canonical specifications and accepted owner decisions as higher authority. Use the installed OpenSpec operation skills only for their owned operations. Never run `openspec init` or create local operation-skill substitutes.

### Delete only after canonical reconciliation and validation

Do not delete candidates during clarification, design, shaping, utility work, or implementation. First reconcile canonical specifications, run strict OpenSpec validation, and show the resulting diff. Then, with exact-path deletion authority, remove only eligible archived directories, validate again, and checkpoint through `zmem-author-commits` when commit authority exists.

## Risks / Trade-offs

- **Semantic audits require judgment and may retain more archives than necessary** → Prefer a visible false negative over destructive false confidence; report blocked reasons for owner resolution.
- **Canonical requirements can appear equivalent while carrying different constraints** → Require scenario-level mappings and preserve normative strength before consolidation.
- **Git provenance can exist outside the locally inspected history window** → Verify exact paths with repository history rather than assuming recoverability from repository presence.
- **The skill can be mistaken for workflow authority** → State exact operation owners and prohibit stage transition, commit, and deletion inference.
- **A fixed inventory assertion will fail when the new skill is added** → Update that unit expectation as the focused executable proof while relying on established generic discovery behavior; add no prose-pinning test or new Gherkin.

## Migration Plan

1. Add and validate the packaged skill assets.
2. Update the focused companion inventory expectation and run RED/GREEN verification.
3. Synchronize the new capability into canonical specifications.
4. Run repository final gates and archive this change.
5. Leave all existing legacy archives untouched; future invocations of the new skill must audit and authorize their own exact targets.

Rollback removes the new companion directory, restores the inventory expectation, and removes the new canonical capability through a separately governed change.

## Open Questions

None.
