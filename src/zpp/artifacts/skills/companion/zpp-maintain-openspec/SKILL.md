---
name: zpp-maintain-openspec
description: Audit legacy OpenSpec archives, plan lossless consolidation of overlapping canonical specifications, and remove only semantically covered exact archive paths after explicit authorization. Use when an owner asks to inspect OpenSpec drift or contradictions, consolidate canonical requirements, assess archived changes for retention, or clean eligible archives without treating history as current authority.
---

# Maintain OpenSpec

Keep canonical specifications coherent while preserving historical evidence and destructive-operation boundaries.

Read [references/maintenance-contract.md](references/maintenance-contract.md) completely before classifying a candidate, planning consolidation, or proposing deletion.

## Establish authority

1. Discover the containing Git worktree and nearest OpenSpec root.
2. Confirm the explicit maintenance outcome. Begin read-only even when cleanup was requested.
3. Treat canonical specifications and accepted owner input as current authority. Treat active changes as mutable change authority and archives as provenance evidence only.
4. Use `zmem-query-memory` to retrieve relevant valid decisions and lessons, then verify them against current specifications and repository evidence.
5. Do not infer workflow-stage, commit, or deletion authority from this skill, repository detection, archive age, a recommendation, or automatic workflow progression.

If canonical specifications must change, require an explicit `zpp-workflow` invocation at `clarify` or already-active end-to-end workflow authority. This companion skill never advances a stage itself.

## Audit before mutation

1. Inventory active changes, canonical specs, archived changes, delta specs, tasks, strict validation state, and Git provenance. Use `rg --files` for bounded discovery, `openspec ... --json` with `jq` for structured state, and exact Git path history for recoverability.
2. Map every archived requirement and scenario to a current canonical destination. Inspect proposal, design, and tasks for accepted content or unresolved work that a delta alone does not reveal.
3. Produce the complete candidate table required by the maintenance contract. Mark each exact path `eligible`, `blocked`, or `retained` and cite its evidence.
4. Expose contradictions, partial synchronization, unique content, ambiguous ownership, and unresolved task state. Never settle an outcome-changing difference by recency or inference.
5. Produce a before-and-after consolidation map when canonical overlap exists. Do not edit until every accepted constraint and scenario has an explicit destination and the owner has resolved material differences.

## Preserve operation owners

Use only the already installed operation skill that owns an OpenSpec action:

- `openspec-explore` for exploration;
- `openspec-propose` for creating a maintenance change;
- `openspec-update-change` for revising its planning artifacts;
- `openspec-apply-change` for implementation tasks;
- `openspec-sync-specs` for synchronizing accepted deltas;
- `openspec-archive-change` for archiving the completed maintenance change.

Never invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or project an operation skill, repair one, or create a substitute operation owner in the repository or elsewhere. If a required skill is absent or unusable, block that operation and direct the owner to root `zpp init` when no integration exists or root `zpp sync` when one exists. Never run either user-scope lifecycle command on the owner's behalf.

## Consolidate losslessly

1. Reconcile canonical specifications only through the active maintenance change.
2. Preserve the full normative strength, constraints, scenarios, and accepted ownership of every source requirement.
3. Consolidate only proven duplication or an accepted ownership move. Do not merge distinct requirements merely to reduce file count.
4. Use the exact installed sync operation when its contract applies, then run strict OpenSpec validation and inspect the canonical diff.
5. Keep all archive candidates intact until canonical reconciliation is green.

## Gate exact-path removal

Recommend removal only when every archived requirement and scenario is represented canonically, no unique accepted content or unresolved task state remains, contradictions are resolved, strict validation passes, and Git can recover the exact path. Git recoverability is necessary evidence, not semantic proof.

Present eligible exact paths and require the owner to authorize those paths by name. A broad instruction such as “clean the archives” does not authorize deletion. After authorization:

1. Reconfirm each named path is archived, eligible, inside the resolved OpenSpec archive root, and unchanged since the audit.
2. Remove only those exact paths. Never use a broad recursive target or include an active change.
3. Show the deletion diff, run strict validation again, and leave every other archive untouched.
4. Invoke `zmem-author-commits` before committing when separate commit authority exists. Do not infer commit authority from deletion authority.

Pause on any stale evidence, widened target, failed validation, unresolved contradiction, or missing authority.
