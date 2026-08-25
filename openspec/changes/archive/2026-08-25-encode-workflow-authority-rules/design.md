## Context

The workflow family currently treats trace-only OpenSpec scenarios as the reverse half of BDD bindings, requires each material stage checkpoint to include its owned diff without explicitly excluding active planning state, and has one terminal path centered on OpenSpec archive. See `proposal.md` for the policy correction.

The OpenSpec CLI requires scenario-bearing requirements for strict delta validation, so this change's own policy examples remain OpenSpec scenarios because no public BDD feature owns them. The new rule applies when an exact executable feature scenario exists.

## Goals / Non-Goals

**Goals:**

- Make BDD acceptance evidence semantic rather than text/count based.
- Make a feature-side binding sufficient to locate normative requirement authority without retaining a duplicate OpenSpec scenario.
- Preserve incremental implementation commits while keeping active planning artifacts out of Git history.
- Provide a recoverable no-archive terminal route for changes fully preserved by zmem.

**Non-Goals:**

- Remove OpenSpec scenarios that have no qualifying BDD owner.
- Treat zmem as current normative behavior authority.
- Add a new persistent coordination state or change Bundler's stored schema.
- Infer commit, deletion, archive, or memory-fold authority.

## Decisions

### Bind BDD from the feature side only

The compact five-field binding remains immediately above each Gherkin scenario. It resolves to an OpenSpec requirement, but OpenSpec does not carry a reverse trace scenario. Formation and verification scan feature bindings by requirement identity, require unique resolution, and reject any corresponding OpenSpec scenario.

Alternative: keep a trace-only OpenSpec scenario. Rejected because it still creates scenario authority in both places and directly conflicts with the owner rule.

### Reject non-behavioral evidence by observation type

Shaping evaluates what the step observes. Literal text equality/search, self-recording, execution-only assertions, and a bare count never establish behavior. A count is allowed only after an independently observed public value, transition, ordering, or failure contract and only when it constrains the same scenario.

Alternative: ban count assertions syntactically. Rejected because counts can be legitimate supplemental constraints and syntax cannot establish their semantic role.

### Exclude active change roots from checkpoint staging

Every playbook and the kernel retain incremental source/test checkpoints. Before message validation or commit, the checkpoint inventory compares staged paths with the current OpenSpec `changeRoot` and blocks on any descendant. Tasks and other planning artifacts are still updated immediately but remain working-tree state. Normal archive moves them to a terminal path that may be committed.

Alternative: delay all commits until finalization. Rejected by the owner's correction and because it loses coherent stage checkpoints.

### Make memory fold an explicit terminal mode of the single-change adapter

`zpps-finalize` classifies terminal preservation. It returns `memory-fold-required` only with complete eligibility evidence. The playbook invokes `zpps-archive-change` in explicit memory-fold mode; that adapter validates a zmem-bearing message, moves the exact active change to a temporary path outside the worktree, creates the authorized implementation/memory commit, inspects it, and deletes the temporary copy only after success. On failure it restores the active change.

The adapter returns `memory-folded` with the inspected commit SHA and no archive path. The kernel audits the committed source paths, invokes the existing durable-owner `zpp lease abandon` release for the exact bundle, labels the release as intentional memory-fold completion, and may return `lifecycle-complete`. No new Bundler persistence field is introduced.

Alternative: call `openspec archive --skip-specs`. Rejected by the owner's explicit choice not to create an OpenSpec archive. Alternative: delete before commit without a recovery copy. Rejected because commit failure would destroy the only planning record.

### Keep memory-fold eligibility conservative

Eligibility is denied for current normative behavior, nested/branching logic, failure contracts, serialization, compatibility, ownership boundaries, or any partially preserved fact. Simple wording and variable changes qualify only when their complete durable rationale fits valid zmem and relevant canonical behavior already remains unchanged.

## Risks / Trade-offs

- **OpenSpec has no reverse scenario link for BDD-owned behavior** → Verify uniqueness by scanning feature-side bindings and canonical requirement identities in both directions.
- **Existing canonical trace scenarios remain during migration** → Update formation/maintenance rules immediately and remove affected legacy traces only through an explicit bounded migration.
- **Active tasks are absent from incremental commits** → Require task status in every stage result and final semantic verification, while preserving the active directory in the working tree.
- **Memory-fold removal could lose planning on commit failure** → Move to a unique temporary recovery path and restore atomically on failure.
- **Lease abandon usually signals incomplete work** → Require exact inspected memory-fold evidence and report a distinct `memory-folded` lifecycle result; ordinary abandon remains unchanged.

## Migration Plan

1. Shape no new BDD for this policy-only change; keep its scenarios in the delta because no feature owns them.
2. Update workflow skills, component contracts, finalization/archive branches, and zmem checkpoint instructions.
3. Update focused source tests and canonical formation/maintenance specifications.
4. Verify incremental commits never stage the active change while tasks continue to advance.
5. Normally archive this non-foldable policy change, then commit its archived planning state.
