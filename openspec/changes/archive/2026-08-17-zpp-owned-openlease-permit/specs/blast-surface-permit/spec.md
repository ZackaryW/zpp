## ADDED Requirements

### Requirement: Declared affected claim before worktree modification
Before performing an operation that modifies a worktree under an established session, ZPP SHALL require an explicit declared affected claim naming the repositories and authorities the operation intends to affect. ZPP SHALL refuse the operation when no claim has been declared and SHALL NOT synthesize, widen, or infer a claim from observed changes, command arguments, or repository layout.

#### Scenario: BDD target — Refuse an undeclared modification
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Refuse an undeclared modification`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Accept a declared claim
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Accept a declared claim`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Leave read-only resolution permit-free
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Leave read-only resolution permit-free`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Closure resolution and lockability evaluation
ZPP SHALL resolve a declared affected claim to its complete closure through the registered authority graph, including authorities reached by parent and dependency relationships that the claim did not name directly. ZPP SHALL evaluate lockability of that closure and SHALL report the resolved closure, every conflict, every blocking owner, and every promotion issue before a permit is acquired.

#### Scenario: BDD target — Expand a claim to its closure
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Expand a claim to its closure`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Report a blocked closure
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Report a blocked closure`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Report a lockable closure
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Report a lockable closure`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Explicit go-ahead before permit acquisition
ZPP SHALL acquire a permit only under an explicit go-ahead for the resolved closure that was reported. ZPP SHALL NOT acquire a permit automatically from a lockable result, a workflow gate, a prior permit, or a stale closure. When the resolved closure changes after evaluation, ZPP SHALL re-evaluate lockability and require a new go-ahead for the changed closure.

#### Scenario: BDD target — Acquire under explicit go-ahead
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Acquire under explicit go-ahead`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Refuse acquisition without go-ahead
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Refuse acquisition without go-ahead`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Invalidate a stale closure
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Invalidate a stale closure`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Explicit unlock as guarantee check
ZPP SHALL release a held permit only through an explicit unlock. The normal unlock SHALL verify the session's boundary safety, drop the held leases, and record reconciliation debt for generated members. A forced unlock SHALL be available for a session that cannot satisfy the boundary check, SHALL require explicit force authority that ZPP validates, SHALL record reconciliation debt, and SHALL NOT be satisfied by a skill instruction, workflow progression, or an implicit default.

#### Scenario: BDD target — Release a boundary-safe session
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Release a boundary-safe session`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: Refuse an unsafe normal unlock
- **WHEN** an explicit unlock targets a session whose boundary is not safe
- **THEN** ZPP refuses the unlock and reports the boundary condition rather than dropping the leases

#### Scenario: BDD target — Require force authority for a forced unlock
- **WHEN** executable behavior is covered by `features/blast_surface_permit/blast_surface_permit.feature::Require force authority for a forced unlock`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: Book debt on a forced unlock
- **WHEN** a forced unlock is requested with explicit force authority
- **THEN** ZPP drops the held leases, records reconciliation debt, and reports both the released session and the recorded debt
