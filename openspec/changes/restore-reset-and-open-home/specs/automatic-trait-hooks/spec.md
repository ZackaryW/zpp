## MODIFIED Requirements

### Requirement: Agent Router-owned hook lifecycle
Root initialization and grouped workflow lifecycle operations SHALL project and remove the selected agent's packaged hook through Agent Router together with the consolidated workflow skill. Install and update SHALL use Agent Router's hook installation contract, removal SHALL use its hook uninstallation contract, and ZPP SHALL NOT write hook destinations directly.

Confirmed product reset SHALL separately inspect every supported agent's packaged `zpp-session` hook in user scope and remove each present ownership-safe hook through Agent Router only after complete reset preflight succeeds. Reset SHALL NOT broaden ordinary grouped workflow removal, target project-scope hooks, or directly mutate a native hook destination.

#### Scenario: Install a complete workflow integration
- **WHEN** a user installs the ZPP workflow integration for a supported agent and scope
- **THEN** Agent Router projects both the consolidated skill and that agent's native hook

#### Scenario: Remove a complete workflow integration
- **WHEN** a user removes an intact Agent Router-owned ZPP workflow integration for a supported agent and scope
- **THEN** Agent Router removes both the consolidated skill and native hook for that scope

#### Scenario: Reset every user-scope hook safely
- **WHEN** confirmed reset preflight proves each supported agent's user-scope ZPP hook absent or ownership-safe removable
- **THEN** reset removes every present selected hook through Agent Router without inspecting or changing project-scope hooks

#### Scenario: Preserve hooks on reset conflict
- **WHEN** any supported agent's selected user-scope hook is modified, unmanaged, ambiguous, conflicting, or cannot be inspected
- **THEN** complete reset aborts before removing any hook or changing OpenLease state
