## ADDED Requirements

### Requirement: BDD-target scenario reconciliation
The OpenSpec maintenance skill SHALL compare canonical OpenSpec scenarios with established BDD feature scenarios before consolidating or removing scenario content. It SHALL replace a duplicated OpenSpec scenario body with an exact target-form scenario only when `features/<capability>/<capability>.feature::<scenario name>` belongs to the same capability owner, traces to the requirement, exists exactly, has scenario-selected executable public-system bindings, and passes relevant verification. The retained target-form scenario SHALL identify the exact feature authority and SHALL NOT repeat its executable steps.

The maintenance skill SHALL preserve every complete OpenSpec scenario that lacks qualifying BDD coverage. It SHALL treat a missing, stale, cross-capability, untraced, recorder-only, capability-wide, wording-only, or unverified feature target as a blocker, and SHALL NOT infer coverage from similar names or prose. Archive preservation mapping SHALL treat verified target-form scenarios as canonical trace plus feature-owned executable behavior and SHALL treat neither source alone as complete.

#### Scenario: Reconcile a covered scenario to its BDD target
- **WHEN** a canonical OpenSpec scenario duplicates behavior verified by an exact same-capability feature scenario and its scenario-selected binding
- **THEN** maintenance replaces the duplicated steps with a target-form scenario naming that exact feature target

#### Scenario: Preserve an uncovered OpenSpec scenario
- **WHEN** a canonical OpenSpec scenario has no qualifying BDD feature target
- **THEN** maintenance retains its complete WHEN/THEN content and does not remove or redirect it

#### Scenario: Reject guessed or insufficient coverage
- **WHEN** a possible feature target matches only by terminology, belongs to another capability, lacks requirement traceability, uses a recorder or capability-wide assertion, or has not passed relevant verification
- **THEN** maintenance leaves the OpenSpec scenario unchanged and reports the exact coverage blocker

#### Scenario: Preserve a targeted archive scenario completely
- **WHEN** an archived current scenario maps to a canonical target-form scenario whose exact BDD feature remains valid and verified
- **THEN** maintenance treats the canonical trace and feature-owned executable behavior together as complete preservation
