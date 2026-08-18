@openlease-session-lifecycle
Feature: Establish a repository session automatically
  ZPP files the minimal topology a blast-surface claim needs, keys the session
  to the worktree unless one is named, and reuses that space on every invocation.
  Registration supplies existence only; a relationship stays an explicit act.

  Scenario: Register an unregistered worktree
    Given a disposable Git worktree matching no registered repository
    When ZPP establishes the session for that worktree
    Then the worktree is registered with one worktree-covering authority
    And an affected claim for that repository resolves against the authority graph

  Scenario: Reuse an existing registration
    Given a disposable Git worktree whose session was already established
    When ZPP establishes the session for that worktree again
    Then the existing repository and authority records are reused
    And no duplicate repository or authority record exists

  Scenario: Leave relationships undeclared by automatic registration
    Given a disposable Git worktree matching no registered repository
    When ZPP establishes the session for that worktree
    Then no parent relationship and no dependency relationship are declared
    And no authority beyond the worktree-covering authority exists

  Scenario: Reuse one session across invocations
    Given a disposable Git worktree with an established session
    When ZPP is invoked again for that worktree without an explicit session name
    Then both invocations report the same session identity and the same session

  Scenario: Establish a session without a host token
    Given a disposable Git worktree and an environment supplying no OpenLease session token
    When ZPP establishes the session for that worktree
    Then session establishment succeeds using the worktree-derived identity

  Scenario: Name a distinct session explicitly
    Given a disposable Git worktree with an established default session
    When a caller establishes a session for that worktree under an explicit session name
    Then that session is distinct from the worktree's default session
    And neither session displaces the other

  Scenario: Establish a session space
    Given a disposable Git worktree with a registered repository
    When ZPP establishes the session for that worktree
    Then one space is held and associated with that repository
    And ZPP reports that space identifier

  Scenario: Supply space-scoped sources without explicit selection
    Given a disposable Git worktree with an established session contributing a space-scoped trait source
    When traits resolve with no explicit space argument and no space environment value
    Then the resolved sources include the established session's space-scoped source

  Scenario: Block an undeclared cross-repository claim
    Given two registered repositories with no declared relationship between them
    When a session for the first repository claims the second repository
    Then the claim is refused
    And the refusal names the relationship declaration required

  Scenario: Permit a declared cross-repository claim
    Given two registered repositories with an explicitly declared dependency relationship
    When a session for the first repository claims the second repository
    Then the claim is accepted and the second repository participates in the affected claim
