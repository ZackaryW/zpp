## MODIFIED Requirements

### Requirement: BDD-target scenario reconciliation
The OpenSpec maintenance skill SHALL compare canonical OpenSpec scenarios with established BDD feature scenarios before consolidating or removing scenario content. It SHALL remove a canonical OpenSpec scenario completely only when the exact feature scenario belongs to the same capability owner, carries a valid feature-side requirement binding, exercises public-system behavior through scenario-selected verification, and has relevant passing evidence. It SHALL retain the normative requirement and SHALL NOT replace the removed scenario with a trace-only or target-form OpenSpec scenario.

The maintenance skill SHALL preserve every complete OpenSpec scenario that lacks qualifying BDD coverage. It SHALL treat a missing, stale, cross-capability, unbound, text-only, recorder-only, pure-counting, or unverified feature target as a blocker and SHALL NOT infer coverage from terminology or prose. Archive preservation mapping SHALL treat the canonical requirement plus exact feature-side binding and executable feature behavior as complete preservation.

#### Scenario: Remove a covered OpenSpec scenario
- **WHEN** a canonical OpenSpec scenario duplicates behavior verified by an exact same-capability feature scenario and valid feature-side requirement binding
- **THEN** maintenance removes the OpenSpec scenario completely and retains no target-form replacement

#### Scenario: Preserve an uncovered OpenSpec scenario
- **WHEN** a canonical OpenSpec scenario has no qualifying BDD feature target
- **THEN** maintenance retains its complete WHEN/THEN content and does not remove or redirect it

#### Scenario: Reject guessed or insufficient coverage
- **WHEN** a possible feature target matches only by terminology, belongs to another capability, lacks requirement traceability, uses text-only or pure-counting evidence, or has not passed relevant verification
- **THEN** maintenance leaves the OpenSpec scenario unchanged and reports the exact coverage blocker

#### Scenario: Preserve BDD-owned behavior without a trace scenario
- **WHEN** an archived current scenario maps to a canonical requirement whose exact bound BDD feature remains valid and verified
- **THEN** maintenance treats the requirement, feature-side binding, and feature-owned behavior together as complete preservation without an OpenSpec scenario

## ADDED Requirements

### Requirement: Recognize memory-folded workflow provenance
The OpenSpec maintenance skill SHALL recognize a workflow terminal result whose active change was intentionally removed without archive because its complete durable content was committed as validated zmem. It SHALL verify the Git commit, zmem entries, eligibility evidence, absence of current normative behavior, and absence of an archive path. It SHALL NOT report the missing archive as loss when all of that evidence is valid, and SHALL NOT use memory as a substitute for current canonical behavior.

#### Scenario: Accept complete memory-fold provenance
- **WHEN** a terminal workflow commit proves validated zmem preservation for an eligible simple change and no current normative behavior was discarded
- **THEN** maintenance accepts the Git and zmem record as complete provenance without requiring an OpenSpec archive

#### Scenario: Reject memory-only normative behavior
- **WHEN** a removed active change contained current behavior, branching, serialization, compatibility, ownership, or another canonical contract
- **THEN** maintenance reports lost OpenSpec authority and does not accept the zmem record as complete preservation
