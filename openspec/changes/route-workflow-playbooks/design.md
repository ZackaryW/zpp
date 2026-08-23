## Context

See `proposal.md` for motivation. The current integration projects one `zpp-workflow` skill and six generated OpenSpec operation skills. The consolidated skill owns the correct lifecycle gates, but it also has to classify every outcome and reconcile operation-skill instructions that can behave like separate top-level workflows. Agent Router already projects packaged skill directories, and the existing `features/consolidated_workflow_skill/` root owns public integration verification.

## Goals / Non-Goals

**Goals:**

- Make complete workflows discoverable by outcome without copying lifecycle policy.
- Give ZPP one shared lifecycle authority and explicit, auditable delegation boundaries.
- Let ZPP use OpenSpec programmatically through bounded planning and archive components.
- Preserve explicit owner decisions, automatic progression limits, Bundler leases, checkpoint authority, and truthful completion.

**Non-Goals:**

- Fork or overwrite OpenSpec's generated skills in place.
- Make a trait, entry skill, or component skill an alternative workflow authority.
- Restore ZPP 1.x `zpp-flow-*` stages or their compatibility behavior.
- Add runtime workflow classes, persist a new workflow-state format, or assert packaged prose in tests.

## Decisions

### Package roles as skills but keep one authority

Every role is packaged as a real skill because that is the unit Agent Router can install and an agent can delegate to. Role semantics, not packaging, determine authority:

| Skill | Role | Authority boundary |
|---|---|---|
| `zpp-auto` | Triage entry | Classifies and delegates; performs no governed mutation |
| `zpp-new-feature` | Feature workflow entry | Selects `feature` and delegates |
| `zpp-fix-bug` | Bug-fix workflow entry | Selects `bugfix` and delegates |
| `zpp-scaffold` | Scaffold workflow entry | Selects `scaffold` and delegates |
| `zpp-workflow` | Generic workflow entry | Accepts an explicit kind or starts clarification |
| `zpp-legacy-workflow` | Compatibility entry | Translates the previous consolidated invocation shape only |
| `zpps-workflow-kernel` | Shared workflow authority | Owns stages, gates, leases, verification, checkpoints, and completion |
| `zpps-plan` | Planning component | Owns only the delegated OpenSpec planning operation |
| `zpps-archive` | Archive component | Owns only the delegated OpenSpec reconciliation and archive operation |

This is preferred over internal reference-only playbooks because each meaningful workflow or phase remains discoverable and independently maintainable. It is preferred over complete per-outcome kernels because shared authority cannot drift.

### Delegate through a structured envelope

Each workflow entry delegates to `zpps-workflow-kernel` with a workflow kind, repository/store target, declared starting stage, automatic-progression authority, accepted owner input, and compatibility mode. The entry validates or supplies only fields it owns. The kernel validates the complete envelope before acting and never treats a skill name as evidence that predecessor gates passed.

Specific entries declare their fixed workflow kind. The generic entry requests an unresolved kind during `clarify`. If no later stage was explicitly selected, an entry declares `clarify`; no entry infers a later stage from OpenSpec state, repository files, or trait context.

### Keep automatic routing conservative

`zpp-auto` classifies only enough to choose an entry. It routes requests that unambiguously describe new behavior, defect correction, or initial scaffolding to the corresponding workflow. Mixed, ambiguous, or outcome-changing requests route to `zpp-workflow` at `clarify`. Triage does not grant mutation, automatic progression, checkpoint commits, or product-decision authority; those fields must come from the owner invocation and are enforced by the kernel.

This is preferred over asking for a workflow name on every request because clear intent can be routed mechanically. Falling back to clarification is preferred over heuristic guesses when classification affects the product contract.

### Own OpenSpec policy in bounded ZPP components

`zpps-plan` owns proposal creation and coherent updates to proposal, delta specifications, design, and tasks. `zpps-archive` owns final validation, canonical reconciliation, and archive execution. They use the installed OpenSpec executable and its public status, instruction, validation, synchronization, and archive interfaces; they do not invoke generated `openspec-*` skills as workflow authorities and do not initialize or rewrite the user's OpenSpec skill installation.

The kernel delegates only the exact operation and receives evidence back. A component cannot select a workflow, waive a predecessor, acquire unrelated lease scope, authorize a commit, or continue to another stage. This preserves ZPP's lifecycle while avoiding contradictory top-level skill instructions.

### Limit the legacy adapter and preserve the verification gate

`zpp-legacy-workflow` translates only the immediately preceding consolidated `zpp-workflow` invocation contract into the structured envelope, then delegates to the same kernel. It contains no copied stage policy and recognizes no `zpp-flow-*` identity. It is eligible for removal only through an owner-approved breaking major release after a documented deprecation period.

The repository behavior-gate identity remains `zpp-workflow`. Every entry reaches the same kernel-owned verification surface, so entry proliferation does not create new repository gate names or capability-wide assertion blocks.

### Verify routing through the public installed surface

Public installation, invocation routing, fallback, and authority rejection belong in the independently runnable `features/consolidated_workflow_skill/` Behave root with scenario-selected bindings. Pure routing and envelope-validation matrices belong in unit tests. Tests inspect skill structure and observed routing outcomes rather than pinning arbitrary instruction wording.

## Risks / Trade-offs

- [More installed skills may look like more authorities] → Give each description an explicit role and rejection boundary, and verify that all lifecycle execution reaches the one kernel.
- [Automatic triage may misclassify mixed work] → Route any non-exclusive classification to generic clarification and perform no mutation during triage.
- [Component skills may accrete workflow policy] → Keep their inputs and outputs operation-bounded and reject stage selection, progression, lease expansion, and completion claims.
- [OpenSpec CLI behavior may change] → Consume its public command and artifact-instruction interfaces, validate observed results, and keep version-specific adaptation inside the bounded components.
- [The legacy adapter may become permanent] → Keep it policy-free and make removal a documented future major-version decision.

## Migration Plan

1. Add failing public routing scenarios and focused unit matrices for the new skill roles.
2. Extract shared lifecycle guidance from `zpp-workflow` into `zpps-workflow-kernel` without changing its authority rules.
3. Add `zpps-plan` and `zpps-archive`, then migrate kernel delegation away from generated OpenSpec operation skills.
4. Add the specific, generic, automatic, and legacy entry skills as thin delegates.
5. Update packaged inventory and Agent Router projection, then run focused and complete repository verification.

Rollback restores the previous packaged skill inventory and consolidated `zpp-workflow` content together; it does not modify repository OpenSpec data or Bundler state.
