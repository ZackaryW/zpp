@zpp-coordination-commands
Feature: Route every coordination operation through ZPP
  ZPP owns the coordination surface an agent needs, so no session locates or
  interrogates the provider executable. Inspection never mutates, destructive
  work needs an argument ZPP validates, and observed state never widens a target.

  Scenario: Perform a coordination operation through ZPP
    Given a disposable Git worktree with an established session
    When a caller performs a supported topology session or permit operation
    Then ZPP executes it through the OpenLease library API
    And no provider executable is located or invoked

  Scenario: Report an unsupported operation
    Given the public coordination command help is available
    When a caller requests a coordination operation ZPP does not expose
    Then ZPP reports the operation as unavailable
    And the report does not direct the caller to the provider executable

  Scenario: Inspect without mutation
    Given a registered topology with an established session and a held permit
    When a caller inspects topology session status closure lockability and a reconciliation plan
    Then the observed state is reported
    And the registered topology sessions leases reconciliations and dispositions are unchanged

  Scenario: Refuse a destructive operation without explicit authority
    Given a session with retained state eligible for cleanup
    When cleanup is requested without the explicit authority argument
    Then the operation is refused
    And the refusal names the authority required
    And no state is changed

  Scenario: Execute a destructive operation under explicit authority
    Given a session with retained state eligible for cleanup
    When cleanup is requested with the explicit authority argument and every target named
    Then exactly that operation is executed and its observed result is reported

  Scenario: Reject an instruction as destructive authority
    Given a session with retained state eligible for cleanup
    When a packaged skill body asserts authority for cleanup without the explicit argument
    Then the operation is refused because only the validated argument satisfies the gate

  Scenario: Refuse an unnamed widened target
    Given a requested operation whose observed state extends beyond its named targets
    When the operation is invoked
    Then the widened portion is refused
    And the report names the additional targets and the authority required
