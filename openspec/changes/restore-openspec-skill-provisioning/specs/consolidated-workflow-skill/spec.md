## ADDED Requirements

### Requirement: Ready installed workflow operation set
A complete user-scope ZPP workflow integration SHALL include the one consolidated `zpp-workflow` authority, the agent-native `zpp-session` trait hook, and the six component-owned OpenSpec operation skills required by that authority. The generated OpenSpec skills SHALL remain separate operation owners and SHALL NOT become additional ZPP workflow stage skills.

#### Scenario: Use OpenSpec operations after initialization
- **WHEN** an agent begins the consolidated workflow after successful root initialization
- **THEN** the agent has the generated OpenSpec operation skills required for proposal, application, synchronization, and archival without a separate ZPP setup step

#### Scenario: Preserve one ZPP workflow authority
- **WHEN** the complete integration contains six OpenSpec operation skills
- **THEN** `zpp-workflow` remains the only ZPP workflow authority and the generated skills remain component operation integrations

