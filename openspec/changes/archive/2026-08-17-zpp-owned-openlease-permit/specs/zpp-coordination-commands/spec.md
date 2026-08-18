## ADDED Requirements

### Requirement: ZPP-owned coordination command surface
ZPP SHALL own the complete coordination command surface an agent uses for OpenLease operations, covering topology registration and relationship declaration, session establishment, affected-claim declaration, closure and lockability inspection, permit acquisition and unlock, successor preparation, reconciliation planning and application, handoff, recovery, abandonment, cleanup, and preparation repair. ZPP SHALL execute these operations through the OpenLease library API. An agent SHALL NOT need to locate the `openlease` executable, read its help output, or assemble provider argv to perform any of them.

#### Scenario: BDD target — Perform a coordination operation through ZPP
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Perform a coordination operation through ZPP`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Report an unsupported operation
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Report an unsupported operation`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Distinct read-only inspection
ZPP SHALL keep topology inspection, session status, closure resolution, lockability evaluation, and reconciliation planning read-only. These operations SHALL NOT register topology, establish a session, acquire or release a permit, apply a reconciliation, or change any successor disposition.

#### Scenario: BDD target — Inspect without mutation
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Inspect without mutation`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: CLI-enforced destructive authority
ZPP SHALL gate abandonment, cleanup, handoff disposition, forced recovery, and preparation rollback behind an explicit authority argument that ZPP itself validates before invoking the operation. A packaged skill instruction, resolved trait body, workflow stage, prior permit, or established session SHALL NOT satisfy that gate. ZPP SHALL name every exact target the operation can change before executing it.

#### Scenario: BDD target — Refuse a destructive operation without explicit authority
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Refuse a destructive operation without explicit authority`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Execute a destructive operation under explicit authority
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Execute a destructive operation under explicit authority`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Reject an instruction as destructive authority
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Reject an instruction as destructive authority`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Refuse widened coordination targets
When observed state widens a requested coordination operation beyond its named targets, ZPP SHALL refuse the widened portion and report the additional targets and authority required. ZPP SHALL NOT silently include an unnamed repository, authority, successor, or reconciliation path.

#### Scenario: BDD target — Refuse an unnamed widened target
- **WHEN** executable behavior is covered by `features/zpp_coordination_commands/zpp_coordination_commands.feature::Refuse an unnamed widened target`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
