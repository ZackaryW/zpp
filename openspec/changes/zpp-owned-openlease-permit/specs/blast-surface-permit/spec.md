## ADDED Requirements

### Requirement: Declared affected claim before worktree modification
Before performing an operation that modifies a worktree under an established session, ZPP SHALL require an explicit declared affected claim naming the repositories and authorities the operation intends to affect. ZPP SHALL refuse the operation when no claim has been declared and SHALL NOT synthesize, widen, or infer a claim from observed changes, command arguments, or repository layout.

#### Scenario: Refuse an undeclared modification
- **WHEN** an operation that modifies the worktree runs under an established session with no declared affected claim
- **THEN** ZPP refuses the operation and reports that an explicit affected claim is required

#### Scenario: Accept a declared claim
- **WHEN** a caller declares an affected claim naming registered repositories and authorities
- **THEN** ZPP records that claim against the established session

#### Scenario: Leave read-only resolution permit-free
- **WHEN** trait resolution or another read-only operation runs under an established session
- **THEN** ZPP performs it without requiring a declared claim or acquiring a lease

### Requirement: Closure resolution and lockability evaluation
ZPP SHALL resolve a declared affected claim to its complete closure through the registered authority graph, including authorities reached by parent and dependency relationships that the claim did not name directly. ZPP SHALL evaluate lockability of that closure and SHALL report the resolved closure, every conflict, every blocking owner, and every promotion issue before a permit is acquired.

#### Scenario: Expand a claim to its closure
- **WHEN** a declared claim names an authority that has dependent authorities in the registered graph
- **THEN** ZPP reports the resolved closure including those dependent authorities rather than only the named authority

#### Scenario: Report a blocked closure
- **WHEN** a resolved closure overlaps an authority leased by another session
- **THEN** ZPP reports the closure as not lockable together with the conflicting authorities and their blocking owners

#### Scenario: Report a lockable closure
- **WHEN** a resolved closure overlaps no authority leased by another session and raises no promotion issue
- **THEN** ZPP reports the closure as lockable together with its complete resolved membership

### Requirement: Explicit go-ahead before permit acquisition
ZPP SHALL acquire a permit only under an explicit go-ahead for the resolved closure that was reported. ZPP SHALL NOT acquire a permit automatically from a lockable result, a workflow gate, a prior permit, or a stale closure. When the resolved closure changes after evaluation, ZPP SHALL re-evaluate lockability and require a new go-ahead for the changed closure.

#### Scenario: Acquire under explicit go-ahead
- **WHEN** an explicit go-ahead is given for a reported lockable closure
- **THEN** ZPP acquires the lease for that closure and the session holds the permit

#### Scenario: Refuse acquisition without go-ahead
- **WHEN** a closure is reported lockable but no explicit go-ahead is given
- **THEN** ZPP acquires no lease and the session holds no permit

#### Scenario: Invalidate a stale closure
- **WHEN** the resolved closure changes between evaluation and acquisition
- **THEN** ZPP refuses to acquire against the earlier closure and requires re-evaluation and a new go-ahead

### Requirement: Explicit unlock as guarantee check
ZPP SHALL release a held permit only through an explicit unlock. The normal unlock SHALL verify the session's boundary safety, drop the held leases, and record reconciliation debt for generated members. A forced unlock SHALL be available for a session that cannot satisfy the boundary check, SHALL require explicit force authority that ZPP validates, SHALL record reconciliation debt, and SHALL NOT be satisfied by a skill instruction, workflow progression, or an implicit default.

#### Scenario: Release a boundary-safe session
- **WHEN** an explicit unlock targets a session whose boundary is safe
- **THEN** ZPP drops the held leases, records reconciliation debt for generated members, and reports the released session

#### Scenario: Refuse an unsafe normal unlock
- **WHEN** an explicit unlock targets a session whose boundary is not safe
- **THEN** ZPP refuses the unlock and reports the boundary condition rather than dropping the leases

#### Scenario: Require force authority for a forced unlock
- **WHEN** a forced unlock is requested without explicit force authority
- **THEN** ZPP refuses the operation and reports that explicit force authority is required

#### Scenario: Book debt on a forced unlock
- **WHEN** a forced unlock is requested with explicit force authority
- **THEN** ZPP drops the held leases, records reconciliation debt, and reports both the released session and the recorded debt
