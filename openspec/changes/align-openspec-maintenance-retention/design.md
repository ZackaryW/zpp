## Context

The first dry run correctly preserved destructive boundaries but applied the original contract literally: it required canonical representation for every archive item and treated unique planning prose or stale task boxes as blockers. That produced a long audit with no eligible paths even when current requirements or repository memory already preserved the useful content.

The owner corrected the product model. OpenSpec is current normative authority; zmem is durable historical decision authority. An archive is redundant when its individual contents are preserved by the appropriate one of those stores. Superseded material receives a capability-relative grace period, and superseded zmem decisions must stop ranking as valid guidance.

## Goals / Non-Goals

**Goals:**

- Classify archive contents by the authority that must preserve them.
- Merge canonical requirements that govern the same behavior.
- Define a deterministic ten-version supersession grace period.
- Cancel superseded valid zmem decisions with exact resolved targets.
- Produce a short actionable result before detailed evidence.

**Non-Goals:**

- Delete an archive in this change.
- Treat zmem as a substitute for missing current normative behavior.
- Merge requirements with different owners or unresolved semantic differences.
- Cancel lessons or guess zmem effect targets.
- Add executable code, scripts, tests, commands, hooks, or OpenSpec skill bootstrap.

## Decisions

### Preserve each item in its proper authority

Classify each accepted archive item independently. Current behavior, constraints, scenarios, serialization, and owner boundaries require a canonical OpenSpec destination. Historical rationale and a superseded decision require a traceable zmem entry. One appropriate destination is sufficient; the audit does not require every planning sentence to be copied into both stores, and a stale checkbox does not block removal when the represented outcome is otherwise proven.

This is an `OR` across appropriate preservation sources, not permission to store current normative behavior only in memory. Missing or ambiguous current behavior still blocks removal until canonicalized.

### Merge same-behavior canonical requirements before cleanup

When two canonical requirements govern the same behavior and owner boundary, form one before/after mapping and merge them into one authoritative destination. Preserve the strongest mutually accepted constraints and every still-current scenario. A stronger phrase that conflicts with current accepted policy is not automatically retained; unresolved semantic or ownership differences block the merge.

Requirements that merely mention the same component while governing different operations remain separate.

### Count capability versions from archived-change history

One version is one later committed archived change whose delta contains the same capability. Order versions by the Git commit that archived each change, not by filename date or arbitrary repository commits. For a superseded item, count only later archives affecting that item’s capability. A multi-capability archive becomes removable only when every superseded item has reached ten later versions; use the minimum satisfied age across its superseded items as the archive gate.

Redundant content that remains current and is already preserved does not wait ten versions. The grace period applies specifically to outdated or superseded specification and archive content.

### Cancel superseded zmem decisions immediately

When current canonical authority or an explicit owner decision proves a valid zmem `DECISION` fully invalid, resolve its exact SHA and one-based annotation index with zmem, add `zmem(CANCEL)[sha, index]` through `zmem-author-commits`, and validate the complete message with deep replay. Cancellation is not delayed by the archive grace period because the entry must stop influencing current reasoning immediately.

Do not manufacture `CANCEL` for a lesson, a partially valid decision, or an unresolved conflict. Use decay only when an earlier decision remains partly valid.

### Lead with the decision

Maintenance output starts with counts and exact next actions: removable now, waiting for the ten-version grace period, requires canonical merge, requires zmem cancellation, or blocked on an owner decision. Put the complete per-path evidence table and mappings afterward as an appendix.

## Risks / Trade-offs

- **zmem could be mistaken for normative authority** → Require current behavior to remain canonical and use zmem only for historical or superseded reasoning.
- **“Strongest” wording could retain obsolete constraints** → Preserve only mutually accepted current constraints; expose conflicts instead of comparing modal verbs mechanically.
- **Archive dates do not totally order same-day changes** → Use the Git commits that archived the changes.
- **One old item in a multi-capability archive delays the whole directory** → Keep exact-path deletion atomic; split historical content only through a separately governed change if needed.
- **Immediate cancellation can hide a still-partly-valid decision** → Require full invalidity and deep zmem validation; otherwise decay or retain.

## Migration Plan

1. Replace the packaged skill and maintenance reference with the new decision tree and reporting order.
2. Synchronize the modified and added canonical requirements.
3. Cancel `248637c#1`, which encodes the superseded canonical-only archive rule, and record the replacement policy.
4. Validate the skill and all OpenSpec artifacts, then archive this change.

Rollback restores the prior skill and canonical requirements and requires a new explicit zmem decision; it does not automatically reactivate a cancelled entry.

## Open Questions

None.
