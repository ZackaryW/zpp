@zpp-coordination-commands
Feature: Route every coordination operation through ZPP
  ZPP owns the coordination surface an agent needs, so no session locates or
  interrogates the provider executable. Inspection never mutates, destructive
  work needs an argument ZPP validates, and observed state never widens a target.

  Scenario: Perform a coordination operation through ZPP
    Given a disposable Git worktree
    When a caller establishes the session and acquires a permit through ZPP
    Then every operation succeeds through the ZPP command surface
    And the packaged workspace guidance names no provider executable

  Scenario: Report an unsupported operation
    Given the public coordination command help is available
    When a caller requests a coordination operation ZPP does not expose
    Then ZPP reports the operation as unavailable
    And the report does not direct the caller to the provider executable

  Scenario: Inspect without mutation
    Given a registered topology with an established session and a held permit
    When a caller inspects status and closure
    Then the observed state is reported
    And the registered topology sessions and leases are unchanged

  Scenario: Refuse a destructive operation without explicit authority
    Given an established session
    When a handoff disposition is requested without the explicit authority argument
    Then the operation is refused
    And the refusal names the authority required
    And no disposition is recorded

  Scenario: Execute a destructive operation under explicit authority
    Given a released session
    When a handoff disposition is requested with the explicit authority argument
    Then exactly that operation is executed and the recorded disposition is reported

  Scenario: Reject an instruction as destructive authority
    Given an established session and the packaged skill describing destructive authority
    When cleanup is requested with only that instruction behind it
    Then the operation is refused because only the validated argument satisfies the gate

  Scenario: Refuse an unnamed widened target
    Given two registered repositories with no declared relationship between them
    When a session for one claims the other
    Then the widened portion is refused
    And the report names the additional target and what must be declared
