@product-home-lifecycle
Feature: Manage one bounded ZPP home
  ZPP gives users one stable home to inspect and one ownership-safe reset
  without treating repositories or agent projects as disposable state.

  Scenario: Route managed state through the selected home
    Given a caller selects an eligible ZPP home
    When an OpenLease-backed ZPP command runs
    Then ZPP uses only that home's openlease child as managed state
    And selecting the home alone creates no directory

  Scenario: Open the selected ZPP home explicitly
    Given the selected eligible ZPP home is absent
    When a user runs zpp open
    Then ZPP creates and natively opens that exact home
    And it reports the resolved home without initializing the openlease child

  Scenario: Require reset confirmation before external inspection
    Given user integrations and OpenLease state may exist
    When a user runs zpp reset without confirmation
    Then ZPP rejects the command before inspecting or changing external state

  Scenario: Reset complete user integration and managed state
    Given every supported agent user integration is absent or ownership-safe removable
    And the selected ZPP home and its openlease child are safe
    When a user runs zpp reset with confirmation
    Then ZPP removes every present user workflow skill and hook through Agent Router
    And ZPP replaces only the selected home's openlease child with fresh state
    And repository project plugin worktree and other home contents remain unchanged

  Scenario: Abort complete reset on a preflight conflict
    Given one supported agent user workflow skill or hook conflicts with its packaged asset
    When a user runs zpp reset with confirmation
    Then ZPP identifies the conflicting agent integration
    And no user workflow integration or OpenLease state is changed

  Scenario: Preserve state when integration removal is incomplete
    Given complete reset preflight succeeds
    When one Agent Router integration removal fails
    Then ZPP attempts every preflighted removal and reports their outcomes
    And the prior OpenLease state remains unchanged
    And a retry accepts already absent integrations and can complete the reset

  Scenario: Reject an unsafe destructive boundary
    Given the selected home or openlease child cannot be proven to be a safe directory boundary
    When a user runs zpp reset with confirmation
    Then ZPP fails before changing an agent integration or filesystem path

