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

### Requirement: Worktree-keyed session identity with explicit override
ZPP SHALL derive the session identity from the worktree and SHALL NOT require or consume a host-supplied `OPENLEASE_SESSION_TOKEN`. Repeated ZPP invocations for one worktree SHALL resolve to the same session. A caller MAY name a session explicitly to obtain a distinct session for the same worktree. ZPP SHALL NOT infer a host agent session identity from process ancestry, inherited environment, or terminal state, because no observable channel identifies a host agent session on every supported platform; concurrent unnamed sessions in one worktree therefore share one session by design.

#### Scenario: Reuse one session across invocations
- **WHEN** ZPP is invoked more than once for the same worktree without an explicit session name
- **THEN** every invocation resolves the same session identity and the same established session

#### Scenario: Require no host token
- **WHEN** ZPP establishes a session in an environment that sets no `OPENLEASE_SESSION_TOKEN`
- **THEN** session establishment succeeds using the worktree-derived identity

#### Scenario: Name a distinct session explicitly
- **WHEN** a caller establishes a session for a worktree under an explicit session name
- **THEN** ZPP establishes a session distinct from that worktree's default session and neither displaces the other

### Requirement: Session space establishment
ZPP SHALL establish the session as an OpenLease space named deterministically from the registered repository, the worktree, and the session identity, and SHALL reuse that space on every later invocation. The session SHALL be an ordinary space rather than a temporary one, because OpenLease clears a space's temporary descriptor as soon as durable configuration binds to it, so a temporary session could not carry space-scoped trait sources. An established session SHALL supply the selected space for space-scoped trait sources without requiring an explicit `--space` argument or `OPENLEASE_SPACE` value.

#### Scenario: Establish a session space
- **WHEN** ZPP establishes a session for a registered worktree
- **THEN** OpenLease holds one space associated with that repository, ZPP reports its identifier, and a later invocation reuses it

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
