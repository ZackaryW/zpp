---
name: zpp-maintain-openspec
description: Audit and remove redundant OpenSpec archives, merge canonical specifications governing the same behavior, age superseded material by later capability versions, and cancel superseded zmem decisions. Use when an owner asks to clean OpenSpec history, reduce duplicate or contradictory specs, assess archived changes, or reconcile current specifications with repository memory.
---

# Maintain OpenSpec

Reduce redundant OpenSpec history without losing current behavior or durable reasoning.

Read [references/maintenance-contract.md](references/maintenance-contract.md) completely before classifying, consolidating, cancelling memory, or proposing deletion.

## Establish authority

1. Discover the containing Git worktree and nearest OpenSpec root.
2. Begin read-only. Treat canonical specifications and accepted owner input as current normative authority, active changes as mutable change authority, zmem as historical decision authority, and archives as redundant provenance candidates.
3. Use `zmem-query-memory` to retrieve valid decisions and lessons, then verify them against current specifications and repository evidence.
4. Do not infer workflow-stage, commit, or deletion authority from this skill, repository detection, archive age, a recommendation, or automatic progression.

If canonical specifications must change, require an explicitly invoked current
complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or
`zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) at
`clarify`, or existing owner-authorized end-to-end playbook execution. This
companion skill never advances a stage itself.

## Decide in this order

1. Inventory active changes, canonical specs, archived deltas, Git archive commits, and relevant zmem. Use `rg --files`, structured `openspec ... --json` with `jq`, and exact Git path history.
2. Classify each accepted archive item:
   - map current behavior, constraints, scenarios, serialization, and owner boundaries to canonical OpenSpec;
   - map historical rationale and superseded decisions to zmem.
3. Treat the appropriate one of those destinations as preservation. Do not require every planning sentence in both stores, let stale task checkboxes block proven preservation, or use zmem instead of canonical current behavior.
4. Find canonical requirements governing the same behavior and owner. Merge them into one destination while preserving every mutually accepted current constraint and scenario. Keep different operations or owners separate and expose unresolved differences.
5. When current authority proves a valid zmem `DECISION` fully superseded, resolve its SHA and one-based index and use `zmem-author-commits` to create a deeply validated `zmem(CANCEL)[sha, index]` effect immediately. Do not cancel lessons, partly valid decisions, or unresolved conflicts; consider deliberate decay for a partly valid decision.
6. For superseded spec or archive items, count later committed archived changes containing the same capability. Require ten later capability versions for every superseded item before removing its archive. Do not impose this delay on redundant content that remains current and is already preserved.
7. Classify each exact archive path as removable now, waiting for version age, requiring canonical merge, requiring zmem cancellation, or blocked on an owner decision.

Report the counts and exact next actions first. Put per-path evidence and mappings in an appendix instead of leading with the complete table.

## Reconcile scenarios with BDD authority

Before merging or removing any scenario content, determine whether an established
BDD scenario owns its executable behavior. Remove the corresponding OpenSpec scenario
completely only when all of these facts are observed:

- `features/<capability>/<capability>.feature::<scenario name>` exists under the
  same capability owner and traces to the canonical requirement;
- bindings select that scenario and exercise the behavior it names through the
  public system; and
- relevant verification for that exact scenario passes.

Treat the canonical requirement and feature-owned behavior together as preservation;
the feature-side binding is the complete trace and OpenSpec retains no surrogate
scenario. Preserve every full OpenSpec WHEN/THEN scenario that
lacks qualifying BDD coverage. Missing, stale, cross-capability, untraced,
recorder-only, execution-only, capability-wide, literal-text-only, pure-counting, or
unverified targets block
consolidation or removal; similar names and prose never establish coverage.

## Preserve operation owners

Use only the already installed skill that owns each OpenSpec operation:

- `zpps-explore` for read-only exploration;
- `zpps-propose-change` for creating a maintenance change;
- `zpps-update-change` for revising planning artifacts;
- `zpps-apply-change` for implementation tasks;
- `zpps-sync-specs` for synchronizing accepted deltas;
- `zpps-verify-change` for the semantic audit; and
- `zpps-archive-change` for archiving one completed maintenance change.

Never invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or project an operation skill, repair one, or create a substitute operation owner anywhere. If a required skill is absent or unusable, block the operation and direct the owner to root `zpp init` when no integration exists or root `zpp sync` when one exists. Never run either user-scope lifecycle command on the owner's behalf.

## Gate exact-path removal

Before deletion, complete required canonical merges, zmem effects, and strict OpenSpec validation. Present removable exact paths and require the owner to authorize those paths by name; “clean the archives” is not exact-path authority.

After authorization:

1. Reconfirm each named path is archived, unchanged, inside the resolved archive root, and still removable under the current evidence.
2. Remove only those paths. Never use a broad recursive target or include an active change.
3. Show the deletion diff, rerun strict validation, and leave every other archive untouched.
4. Invoke `zmem-author-commits` before committing when separate commit authority exists. Deletion authority never implies commit authority.

Pause on stale evidence, a widened target, failed validation, unresolved current behavior, semantic or ownership conflict, or missing authority.
