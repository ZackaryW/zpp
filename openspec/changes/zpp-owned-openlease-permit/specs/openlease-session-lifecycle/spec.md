## ADDED Requirements

### Requirement: Automatic single-repository floorplan registration
When ZPP establishes a session for a Git worktree whose common directory matches no registered OpenLease repository, ZPP SHALL register that repository and one authority covering the worktree before session establishment continues. ZPP SHALL derive the repository and authority identifiers deterministically from the worktree so repeated establishment is idempotent. ZPP SHALL NOT declare parent relationships, dependency relationships, or additional authorities as part of automatic registration.

#### Scenario: Register an unregistered worktree
- **WHEN** ZPP establishes a session for a Git worktree that matches no registered OpenLease repository
- **THEN** ZPP registers that repository and one worktree-covering authority, and the resulting authority graph resolves an affected claim for that repository

#### Scenario: Reuse existing registration
- **WHEN** ZPP establishes a session for a worktree whose common directory already matches exactly one registered repository
- **THEN** ZPP reuses that registration and creates no duplicate repository or authority record

#### Scenario: Leave relationships undeclared
- **WHEN** automatic registration completes for a single repository
- **THEN** ZPP declares no parent relationship, dependency relationship, or authority beyond the worktree-covering authority

### Requirement: ZPP-derived persisted session identity
ZPP SHALL derive and persist its own session identity for session establishment and SHALL NOT require or consume a host-supplied `OPENLEASE_SESSION_TOKEN`. Repeated ZPP invocations within one host agent session SHALL resolve to the same session identity, and distinct concurrent host agent sessions in one worktree SHALL resolve to distinct session identities.

#### Scenario: Reuse one session across invocations
- **WHEN** ZPP is invoked more than once within a single host agent session in one worktree
- **THEN** every invocation resolves the same session identity and the same established session

#### Scenario: Separate concurrent host sessions
- **WHEN** two concurrent host agent sessions establish sessions in the same worktree
- **THEN** ZPP resolves a distinct session identity for each and neither displaces the other

#### Scenario: Require no host token
- **WHEN** ZPP establishes a session in an environment that sets no `OPENLEASE_SESSION_TOKEN`
- **THEN** session establishment succeeds using the ZPP-derived identity

### Requirement: Temporary-space session establishment
ZPP SHALL establish the session as an OpenLease temporary space keyed to the registered repository, the worktree, and the ZPP-derived session identity. An established session SHALL supply the selected space for space-scoped trait sources without requiring an explicit `--space` argument or `OPENLEASE_SPACE` value.

#### Scenario: Establish a temporary session space
- **WHEN** ZPP establishes a session for a registered worktree
- **THEN** OpenLease holds a temporary space for that repository, worktree, and session identity, and ZPP reports its identifier

#### Scenario: Supply space-scoped sources without explicit selection
- **WHEN** trait resolution runs under an established session and receives no `--space` argument and no `OPENLEASE_SPACE` value
- **THEN** ZPP resolves space-scoped sources from the established session's space

### Requirement: Relationship-gated multi-repository work
ZPP SHALL require explicitly declared relationships — parent relationships, dependency relationships, or additional registered authorities — before a session may affect a repository other than its own worktree. ZPP SHALL NOT infer a relationship from automatic registration, worktree adjacency, or filesystem layout.

#### Scenario: Block an undeclared cross-repository claim
- **WHEN** a session claims a repository for which no relationship has been explicitly declared
- **THEN** ZPP refuses the claim and reports the relationship declaration required

#### Scenario: Permit a declared cross-repository claim
- **WHEN** a parent or dependency relationship has been explicitly declared between the session's repository and another registered repository
- **THEN** ZPP permits that repository to participate in the session's affected claim
