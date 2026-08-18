## ADDED Requirements

### Requirement: Automatic single-repository floorplan registration
When ZPP establishes a session for a Git worktree whose common directory matches no registered OpenLease repository, ZPP SHALL register that repository and one authority covering the worktree before session establishment continues. ZPP SHALL derive the repository and authority identifiers deterministically from the worktree so repeated establishment is idempotent. ZPP SHALL NOT declare parent relationships, dependency relationships, or additional authorities as part of automatic registration.

#### Scenario: BDD target — Register an unregistered worktree
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Register an unregistered worktree`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Reuse an existing registration
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Reuse an existing registration`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Leave relationships undeclared by automatic registration
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Leave relationships undeclared by automatic registration`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Worktree-keyed session identity with explicit override
ZPP SHALL derive the session identity from the worktree and SHALL NOT require or consume a host-supplied `OPENLEASE_SESSION_TOKEN`. Repeated ZPP invocations for one worktree SHALL resolve to the same session. A caller MAY name a session explicitly to obtain a distinct session for the same worktree. ZPP SHALL NOT infer a host agent session identity from process ancestry, inherited environment, or terminal state, because no observable channel identifies a host agent session on every supported platform; concurrent unnamed sessions in one worktree therefore share one session by design.

#### Scenario: BDD target — Reuse one session across invocations
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Reuse one session across invocations`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Establish a session without a host token
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Establish a session without a host token`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Name a distinct session explicitly
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Name a distinct session explicitly`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Session space establishment
ZPP SHALL establish the session as an OpenLease space named deterministically from the registered repository, the worktree, and the session identity, and SHALL reuse that space on every later invocation. The session SHALL be an ordinary space rather than a temporary one, because OpenLease clears a space's temporary descriptor as soon as durable configuration binds to it, so a temporary session could not carry space-scoped trait sources. An established session SHALL supply the selected space for space-scoped trait sources without requiring an explicit `--space` argument or `OPENLEASE_SPACE` value.

#### Scenario: BDD target — Establish a session space
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Establish a session space`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Supply space-scoped sources without explicit selection
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Supply space-scoped sources without explicit selection`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Relationship-gated multi-repository work
ZPP SHALL require explicitly declared relationships — parent relationships, dependency relationships, or additional registered authorities — before a session may affect a repository other than its own worktree. ZPP SHALL NOT infer a relationship from automatic registration, worktree adjacency, or filesystem layout.

#### Scenario: BDD target — Block an undeclared cross-repository claim
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Block an undeclared cross-repository claim`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Permit a declared cross-repository claim
- **WHEN** executable behavior is covered by `features/openlease_session_lifecycle/openlease_session_lifecycle.feature::Permit a declared cross-repository claim`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
