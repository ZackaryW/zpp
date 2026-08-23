## MODIFIED Requirements

### Requirement: Initialization-only OpenSpec provisioning
Root `zpp init` SHALL remain the only operation that initially generates and projects the six OpenSpec operation skills, and root `zpp sync` SHALL regenerate them for existing integrations. Projection order SHALL be `zpp-workflow`, `zpp-traits`, every remaining packaged companion skill in deterministic order, then the canonical generated skills. The removed `zpp-workspace-management` companion and `zpp-session` hook identity SHALL NOT be discovered, projected, removed, or aliased.

#### Scenario: Initialize a ready workflow integration
- **WHEN** root initialization succeeds for selected uninitialized agents
- **THEN** Agent Router installs the workflow, `zpp-traits` hook, remaining companions, and all six generated OpenSpec skills

#### Scenario: Keep grouped workflow lifecycle bounded
- **WHEN** a caller installs, updates, or removes the grouped workflow integration
- **THEN** ZPP manages only the consolidated workflow skill and `zpp-traits` hook for that scope
