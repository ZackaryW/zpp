## MODIFIED Requirements

### Requirement: Complete agreement reconciliation before convergence
During clarification, `zpps-clarify` SHALL classify each newer owner prompt as an explicit confirmation, correction, recommendation, exploration, or deferral and SHALL reconcile it against canonical specifications, the complete older accepted owner input for the current change, the proposal, every capability delta, downstream checkpoints, current repository evidence, and relevant effective repository context before changing normative behavior. A newer statement SHALL NOT silently replace or contradict an older accepted statement merely because it is newer. Assistant recommendations, inferred preferences, default choices, and automatic end-to-end progression alone SHALL NOT count as owner confirmation of an unresolved Clarify decision.

For every outcome-changing decision that remains unresolved after that reconciliation, `zpps-clarify` SHALL ask the owner one to three focused questions at a time unless the active playbook supplies applicable best-decision or full-authority delegation. Each question SHALL identify the exact missing decision and its meaningful consequences; when bounded alternatives exist, it SHALL present concrete mutually exclusive choices, and otherwise it SHALL ask one precise open question. `zpps-clarify` SHALL use the active agent's structured user-question mechanism when available and SHALL ask the same focused question directly when it is unavailable. It SHALL wait for an explicit owner answer and SHALL NOT treat a vague request, an unanswered recommendation, or a presumed default as resolution.

When an apparent agreement conflicts with older accepted input or leaves a product behavior, constraint, serialization, owner boundary, or repository-context gap unsettled, `zpps-clarify` SHALL record the contradiction under `Unresolved — Do Not Assume`, remove the unconfirmed outcome from normative deltas, ask the focused owner question needed to resolve it when decision authority is absent, and keep clarification open. The unresolved record SHALL NOT substitute for asking or for an explicit delegated decision. After each owner answer or delegated decision, `zpps-clarify` SHALL reconcile the complete agreement again and repeat the question loop until no outcome-changing owner decision remains. If downstream feature, utility, wiring, specification, or verification gates were formed from an unconfirmed or superseded outcome, `zpps-clarify` SHALL invalidate them and require replacement gates after clarification converges.

#### Scenario: Keep a recommendation unresolved
- **WHEN** the owner describes one design as a recommendation without explicitly confirming it or delegating the decision
- **THEN** `zpps-clarify` records that preference as unresolved, asks the focused question needed for confirmation, and does not promote it into a normative capability delta

#### Scenario: Reconcile a newer correction with older input
- **WHEN** a newer prompt changes one part of the design while older accepted requirements remain in force
- **THEN** `zpps-clarify` reconciles both across the proposal and every affected delta and asks about any remaining contradiction before continuing

#### Scenario: Refuse automatic progression as decision authority
- **WHEN** the owner authorizes automatic end-to-end progression while a product decision remains unresolved and supplies no applicable decision delegation
- **THEN** the playbook pauses at Clarify and asks the owner rather than choosing the decision merely to continue

#### Scenario: Invalidate a gate built from an assumption
- **WHEN** a downstream gate was formed from an agent-inferred decision that the owner did not confirm or delegate
- **THEN** `zpps-clarify` marks that gate superseded and requires replacement evidence after clarification converges

#### Scenario: Ask a bounded focused question
- **WHEN** repository evidence leaves an outcome-changing decision with bounded alternatives unresolved
- **THEN** `zpps-clarify` asks one focused question with concrete mutually exclusive choices and meaningful consequences instead of making a vague clarification request

#### Scenario: Fall back from an unavailable question mechanism
- **WHEN** the active agent does not expose a structured user-question mechanism
- **THEN** `zpps-clarify` asks the same focused question directly, waits for an explicit answer, and does not weaken or bypass clarification

#### Scenario: Repeat until clarification converges
- **WHEN** an owner answer resolves one question but another outcome-changing decision remains unresolved
- **THEN** `zpps-clarify` reconciles the complete agreement and asks the next focused question batch before declaring clarification complete

#### Scenario: Avoid asking about established evidence
- **WHEN** current specifications, accepted input, and repository evidence already settle a possible clarification point
- **THEN** `zpps-clarify` preserves that established outcome and does not ask the owner to decide it again

## ADDED Requirements

### Requirement: Explicit automatic decision authority
The active playbook SHALL distinguish automatic progression from decision authority. An unambiguous request to proceed automatically SHALL authorize end-to-end continuation and SHALL cover ordinary in-scope component confirmations after the exact proposed effects are shown, but SHALL NOT resolve an outcome-changing Clarify decision. Automatic progression combined with an unambiguous request to make best decisions SHALL authorize the agent to resolve the current or next Clarify gate and SHALL expire when that gate completes. An unambiguous full-authority statement SHALL authorize Clarify decisions and end-to-end continuation across later Clarify re-entry until the owner revokes it.

Revocation SHALL apply to future actions without undoing completed work. No automatic progression, best-decision delegation, full-authority statement, mutation authority, or checkpoint authority SHALL authorize Git push, a GitHub merge action, or access to or mutation of a cloud environment. Each protected operation SHALL require separate step-by-step owner authorization.

#### Scenario: Pause automatic progression at Clarify
- **WHEN** automatic progression reaches an unresolved Clarify gate without applicable decision authority
- **THEN** the playbook pauses for an explicit owner answer and resumes end-to-end progression only after that gate completes

#### Scenario: Consume one-gate best-decision authority
- **WHEN** automatic progression includes best-decision authority and the agent resolves the current or next Clarify gate
- **THEN** the playbook consumes that decision authority when the gate completes and requires the owner at any later Clarify re-entry

#### Scenario: Preserve full authority across Clarify re-entry
- **WHEN** the owner grants unambiguous full authority and a later contradiction returns the workflow to Clarify before revocation
- **THEN** the playbook may resolve the new Clarify gate and continue end to end under the still-active delegation

#### Scenario: Revoke persistent authority prospectively
- **WHEN** the owner revokes full authority
- **THEN** the playbook requires owner decisions at later Clarify gates without attempting to undo already completed work

#### Scenario: Cover ordinary component confirmations
- **WHEN** automatic progression is active and an in-scope component has shown its exact proposed effects
- **THEN** the playbook treats the ordinary component confirmation as supplied without creating another owner gate

#### Scenario: Preserve protected-operation gates
- **WHEN** any workflow authority mode encounters a Git push, GitHub merge action, or cloud-environment operation
- **THEN** the workflow pauses and obtains separate step-by-step owner authorization before that exact operation

### Requirement: Repository-context gap assessment during Clarify
`zpps-clarify` SHALL inspect relevant effective repository context and classify trait coverage as `not-applicable`, `covered`, or `trait-authoring-required`. The assessment SHALL remain read-only, SHALL identify the concrete missing context when authoring is required, and SHALL NOT invoke `zpp-author-trait`, edit a trait document, grant workflow authority, or treat a selected trait as decision evidence. Actual trait authoring SHALL remain a separate explicit operation.

#### Scenario: Report covered repository context
- **WHEN** effective repository context already supplies the guidance required by the accepted change
- **THEN** `zpps-clarify` reports `covered` and asks no trait-authoring question

#### Scenario: Report an actionable context gap
- **WHEN** the accepted change depends on repository guidance that effective context does not supply
- **THEN** `zpps-clarify` reports `trait-authoring-required` with the concrete gap and leaves authoring to a separate explicit operation

#### Scenario: Avoid irrelevant trait work
- **WHEN** repository traits cannot affect the accepted change
- **THEN** `zpps-clarify` reports `not-applicable` without resolving or authoring a trait
