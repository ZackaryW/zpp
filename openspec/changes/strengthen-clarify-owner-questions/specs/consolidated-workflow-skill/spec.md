## MODIFIED Requirements

### Requirement: Complete agreement reconciliation before convergence
During clarification, the consolidated workflow skill SHALL classify each newer owner prompt as an explicit confirmation, correction, recommendation, exploration, or deferral and SHALL reconcile it against canonical specifications, the complete older accepted owner input for the current change, the proposal, every capability delta, downstream checkpoints, and current repository evidence before changing normative behavior. A newer statement SHALL NOT silently replace or contradict an older accepted statement merely because it is newer. Assistant recommendations, inferred preferences, default choices, and automatic end-to-end delegation SHALL NOT count as owner confirmation.

For every outcome-changing decision that remains unresolved after that reconciliation, the skill SHALL ask the owner one to three focused questions at a time. Each question SHALL identify the exact missing decision and its meaningful consequences; when bounded alternatives exist, it SHALL present concrete mutually exclusive choices, and otherwise it SHALL ask one precise open question. The skill SHALL use the active agent's structured user-question mechanism when available and SHALL ask the same focused question directly when it is unavailable. It SHALL wait for an explicit owner answer and SHALL NOT treat a vague request such as “can you clarify?”, an unanswered recommendation, or a presumed default as resolution.

When an apparent agreement conflicts with older accepted input or leaves a product behavior, constraint, serialization, or owner boundary unsettled, the skill SHALL record the contradiction under `Unresolved — Do Not Assume`, remove the unconfirmed outcome from normative deltas, ask the focused owner question needed to resolve it, and keep clarification open. The unresolved record SHALL NOT substitute for asking. After each explicit owner answer, the skill SHALL reconcile the complete agreement again and SHALL repeat the question loop until no outcome-changing owner decision remains. If downstream feature, utility, wiring, or specification gates were formed from an unconfirmed outcome, the skill SHALL invalidate them and require replacement gates after explicit owner confirmation.

#### Scenario: Keep a recommendation unresolved
- **WHEN** the owner describes one design as a recommendation without explicitly confirming its complete public contract
- **THEN** the skill records that preference as unresolved, asks the focused question needed for confirmation, and does not promote it into a normative capability delta

#### Scenario: Reconcile a newer correction with older input
- **WHEN** a newer prompt changes one part of the design while older accepted requirements remain in force
- **THEN** the skill reconciles both across the proposal and every affected delta and asks about any remaining contradiction before continuing

#### Scenario: Refuse automatic delegation as design authority
- **WHEN** the owner authorizes automatic end-to-end execution while a product decision remains unresolved
- **THEN** the skill pauses at clarification and asks the owner rather than choosing the decision in order to continue

#### Scenario: Invalidate a gate built from an assumption
- **WHEN** a downstream feature contract was formed from an assistant-inferred decision that the owner did not confirm
- **THEN** the skill marks that gate superseded and requires a replacement feature checkpoint after clarification converges

#### Scenario: Ask a bounded focused question
- **WHEN** repository evidence leaves an outcome-changing decision with bounded alternatives unresolved
- **THEN** the skill asks one focused question with concrete mutually exclusive choices and meaningful consequences instead of making a vague clarification request

#### Scenario: Fall back from an unavailable question mechanism
- **WHEN** the active agent does not expose a structured user-question mechanism
- **THEN** the skill asks the same focused question directly, waits for an explicit answer, and does not weaken or bypass clarification

#### Scenario: Repeat until clarification converges
- **WHEN** an owner answer resolves one question but another outcome-changing decision remains unresolved
- **THEN** the skill reconciles the complete agreement and asks the next focused question batch before declaring clarification complete

#### Scenario: Avoid asking about established evidence
- **WHEN** current specifications, accepted input, and repository evidence already settle a possible clarification point
- **THEN** the skill preserves that established outcome and does not ask the owner to decide it again
