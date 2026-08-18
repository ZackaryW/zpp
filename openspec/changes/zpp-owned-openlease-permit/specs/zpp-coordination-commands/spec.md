## ADDED Requirements

### Requirement: ZPP-owned coordination command surface
ZPP SHALL own the complete coordination command surface an agent uses for OpenLease operations, covering topology registration and relationship declaration, session establishment, affected-claim declaration, closure and lockability inspection, permit acquisition and unlock, successor preparation, reconciliation planning and application, handoff, recovery, abandonment, cleanup, and preparation repair. ZPP SHALL execute these operations through the OpenLease library API. An agent SHALL NOT need to locate the `openlease` executable, read its help output, or assemble provider argv to perform any of them.

#### Scenario: Perform a coordination operation through ZPP
- **WHEN** an agent performs any supported topology, session, permit, successor, reconciliation, or disposition operation
- **THEN** ZPP exposes a command for it and executes it through the OpenLease library API without the agent invoking the `openlease` executable

#### Scenario: Report an unsupported operation
- **WHEN** a requested coordination operation has no ZPP command
- **THEN** ZPP reports the operation as unavailable rather than directing the caller to the underlying provider executable

### Requirement: Distinct read-only inspection
ZPP SHALL keep topology inspection, session status, closure resolution, lockability evaluation, and reconciliation planning read-only. These operations SHALL NOT register topology, establish a session, acquire or release a permit, apply a reconciliation, or change any successor disposition.

#### Scenario: Inspect without mutation
- **WHEN** a caller inspects topology, session status, a resolved closure, lockability, or a reconciliation plan
- **THEN** ZPP reports the observed state and changes no registered topology, session, lease, reconciliation, or disposition

### Requirement: CLI-enforced destructive authority
ZPP SHALL gate abandonment, cleanup, handoff disposition, forced recovery, and preparation rollback behind an explicit authority argument that ZPP itself validates before invoking the operation. A packaged skill instruction, resolved trait body, workflow stage, prior permit, or established session SHALL NOT satisfy that gate. ZPP SHALL name every exact target the operation can change before executing it.

#### Scenario: Refuse a destructive operation without explicit authority
- **WHEN** an abandonment, cleanup, handoff, forced recovery, or preparation rollback is requested without the explicit authority argument
- **THEN** ZPP refuses the operation and reports the authority required, changing no state

#### Scenario: Execute a destructive operation under explicit authority
- **WHEN** the same operation is requested with the explicit authority argument and every target is named
- **THEN** ZPP executes exactly that operation and reports the observed result

#### Scenario: Reject an instruction as authority
- **WHEN** a packaged skill body, trait body, or workflow stage asserts authority for a destructive operation without the explicit argument
- **THEN** ZPP refuses the operation, because only the validated argument satisfies the gate

### Requirement: Refuse widened coordination targets
When observed state widens a requested coordination operation beyond its named targets, ZPP SHALL refuse the widened portion and report the additional targets and authority required. ZPP SHALL NOT silently include an unnamed repository, authority, successor, or reconciliation path.

#### Scenario: Refuse an unnamed widened target
- **WHEN** observed state extends a requested operation to a repository, authority, successor, or reconciliation path the caller did not name
- **THEN** ZPP refuses the widened portion and reports those targets and the authority required
