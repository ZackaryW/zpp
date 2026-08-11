## ADDED Requirements

### Requirement: Complete agreement reconciliation before convergence
During clarification, the consolidated workflow skill SHALL classify each newer owner prompt as an explicit confirmation, correction, recommendation, exploration, or deferral and SHALL reconcile it against canonical specifications, the complete older accepted owner input for the current change, the proposal, and every capability delta before changing normative behavior. A newer statement SHALL NOT silently replace or contradict an older accepted statement merely because it is newer. Assistant recommendations, inferred preferences, and automatic end-to-end delegation SHALL NOT count as owner confirmation.

When an apparent agreement conflicts with older accepted input or leaves a public behavior branch unsettled, the skill SHALL record the contradiction under `Unresolved — Do Not Assume`, remove the unconfirmed outcome from normative deltas, and keep clarification open. If downstream feature, utility, wiring, or specification gates were formed from the unconfirmed outcome, the skill SHALL invalidate them and require replacement gates after explicit owner confirmation.

#### Scenario: Keep a recommendation unresolved
- **WHEN** the owner describes one design as a recommendation without explicitly confirming its complete public contract
- **THEN** the skill records that preference as unresolved and does not promote it into a normative capability delta

#### Scenario: Reconcile a newer correction with older input
- **WHEN** a newer prompt changes one part of the design while older accepted requirements remain in force
- **THEN** the skill reconciles both across the proposal and every affected delta and exposes any contradiction before continuing

#### Scenario: Refuse automatic delegation as design authority
- **WHEN** the owner authorizes automatic end-to-end execution while a product decision remains unresolved
- **THEN** the skill pauses at clarification rather than choosing the decision in order to continue

#### Scenario: Invalidate a gate built from an assumption
- **WHEN** a downstream feature contract was formed from an assistant-inferred decision that the owner did not confirm
- **THEN** the skill marks that gate superseded and requires a replacement feature checkpoint after clarification converges

## MODIFIED Requirements

### Requirement: Explicit stage actions
The consolidated workflow skill SHALL require the agent to declare an explicit current stage for each workflow invocation and SHALL NOT infer it from OpenSpec status, repository files, stored descriptive context, or trait output. When automatic continuation is separately authorized and the complete current-stage contract has converged, the skill SHALL expose and execute each next stage as a distinct stage action. Trait resolution SHALL NOT select or advance a workflow stage.

#### Scenario: Reject an unnamed stage
- **WHEN** a workflow invocation does not identify the requested stage
- **THEN** the skill requests that stage rather than inferring one from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes or truthfully skips one conditional stage and continues
- **THEN** the skill declares the next stage explicitly without delegating stage choice to the trait hook

### Requirement: Agent-declared stage outcomes
For `shape`, `plan-utilities`, `mature-utilities`, `wire`, and `form-specs`, the acting agent SHALL declare either `completed` or `skipped: not applicable`. The consolidated workflow skill SHALL accept a skip only after independently observing the stage-specific evidence that no owned output is required. A selected trait, derived context value, repository declaration, or failed command SHALL NOT establish a skip. `clarify` and `finalize` SHALL remain mandatory and SHALL NOT accept a not-applicable outcome.

#### Scenario: Skip feature shaping without public behavior
- **WHEN** the agent declares shape not applicable and the accepted change has no public or integration behavior requiring an executable feature contract
- **THEN** the skill records `skipped: not applicable` and hands off to utility planning without creating a feature

#### Scenario: Run a stage when evidence is uncertain
- **WHEN** an agent proposes a conditional-stage skip but the stage-specific evidence does not prove that no owned output is required
- **THEN** the skill runs the stage normally instead of accepting the skip

#### Scenario: Reject a failed-stage skip
- **WHEN** a stage command or verification fails
- **THEN** the skill diagnoses or reports the failed gate and does not relabel it as not applicable

#### Scenario: Require mandatory boundary stages
- **WHEN** the workflow begins clarification or reaches finalization
- **THEN** the skill performs that stage and rejects a not-applicable declaration
