## MODIFIED Requirements

### Requirement: Confirmed complete product reset
Root `zpp reset` SHALL require `--yes` before inspecting or mutating external state. A confirmed reset SHALL target every supported agent's ZPP-owned `zpp-workflow` skill, every discovered packaged companion skill, `zpp-session` hook, and six canonical ZPP-provisioned OpenSpec operation skills in user scope, prepare fresh OpenLease state, remove every selected asset through Agent Router, and replace only the selected home's `openlease` child after projection cleanup succeeds. Reset SHALL apply ordinary complete preflight and ownership-safe removal to the packaged ZPP skills and native hook. It SHALL force-delete only the canonical OpenSpec skills by stable name under Agent Router's explicit forced-owned deletion contract, retain no backup or history for them, and SHALL NOT invoke OpenSpec generation. It SHALL NOT expose or accept the former `--overwrite-global-traits` option.

#### Scenario: Reject unconfirmed reset
- **WHEN** a caller invokes `zpp reset` without `--yes`
- **THEN** ZPP rejects the command before inspecting agent projections, preparing state, or changing the filesystem

#### Scenario: Reset complete user integration and state
- **WHEN** a caller confirms reset, existing preflight passes, and every selected removal succeeds or is already absent
- **THEN** ZPP removes all present ZPP-owned user workflow, companion, OpenSpec operation skills, and hooks through Agent Router and replaces the exact OpenLease state child with fresh state

#### Scenario: Target every discovered companion skill
- **WHEN** a caller confirms reset and the packaged companion inventory contains skills beyond the packaged authoring pair
- **THEN** reset targets every discovered companion skill for each supported agent without requiring a declared list of skill names

#### Scenario: Force-delete modified generated skills
- **WHEN** a confirmed reset encounters a modified canonical OpenSpec skill with valid matching Agent Router ownership
- **THEN** Agent Router deletes that exact skill and its ownership state without backup or OpenSpec regeneration

#### Scenario: Omit obsolete global-trait replacement
- **WHEN** a caller inspects reset help or supplies the former overwrite option
- **THEN** ZPP exposes no global-trait overwrite mode and rejects the unsupported option

### Requirement: Complete reset preflight and retry safety
Before any reset mutation, ZPP SHALL inspect every supported agent's user-scope `zpp-session` hook, `zpp-workflow` skill, and every discovered packaged companion skill through Agent Router, validate the selected home and exact state child, and prepare replacement OpenLease state. An absent preflighted projection SHALL be eligible and require no standard removal. Any modified, unmanaged, ambiguous, conflicting, unknown, or failed preflight inspection SHALL abort the complete reset without removing any projection or replacing state.

After successful preflight, ZPP SHALL attempt the standard preflighted removals and forced canonical OpenSpec skill removals in deterministic supported-agent and within-agent asset order and SHALL aggregate runtime failures. Within each agent, standard removal SHALL follow hook, workflow skill, then every packaged companion skill in the deterministic packaged order, before forced OpenSpec removals. Forced OpenSpec removal SHALL treat a wholly absent skill and ownership record as an eligible no-op, remove modified content only with valid matching Agent Router ownership, and reject a present unmanaged target or invalid ownership. Any removal failure SHALL leave the prior OpenLease state unchanged. Earlier successful removals MAY remain removed; a retry SHALL treat already absent assets as eligible and SHALL converge without adopting or directly deleting native assets.

#### Scenario: Abort on one projection conflict
- **WHEN** any selected user-scope workflow skill, packaged companion skill, or hook is not absent or ownership-safe removable during preflight
- **THEN** reset identifies the agent and asset and changes no selected projection or OpenLease state

#### Scenario: Preserve state after runtime removal failure
- **WHEN** standard preflight succeeds but one standard or forced Agent Router removal fails
- **THEN** reset attempts the remaining planned removals, reports all outcomes, leaves prior OpenLease state unchanged, and does not claim completion

#### Scenario: Reject an unmanaged same-named OpenSpec skill
- **WHEN** forced reset cleanup encounters a present canonical OpenSpec skill without valid matching Agent Router ownership
- **THEN** Agent Router preserves that skill, reset reports the conflict, and OpenLease state is not replaced

#### Scenario: Retry after partial cleanup
- **WHEN** reset is retried after an earlier runtime failure removed some selected projections
- **THEN** absent assets are eligible, remaining owned assets are removed through Agent Router, and state replacement occurs only after cleanup succeeds
