@product-home-lifecycle
Feature: Manage one bounded ZPP integration lifecycle
  ZPP gives users one stable home, one command to create an integration, one to
  repair it, and one ownership-safe reset, without treating repositories or
  agent projects as disposable state. Ownership and destructive-boundary rules
  are canonical requirements verified by inspection, not scenarios.

  Scenario: Open the selected ZPP home explicitly
    Given a temporary user environment
    When a user opens an absent selected ZPP home
    Then ZPP creates and natively opens that exact home
    And it does not initialize the openlease child

  Scenario: Require reset confirmation before external inspection
    Given a temporary user environment
    When a user runs reset without confirmation
    Then ZPP rejects the command and names the required confirmation

  Scenario: Summarize reset unless JSON is requested
    Given a temporary user environment
    When a user runs confirmed reset with and without JSON output
    Then the default reset result is one concise line
    And the JSON reset result reports the replaced state

  Scenario: Initialize an agent that carries no projection
    Given a temporary user environment
    When a user initializes the codex agent
    Then every packaged and generated integration entry is installed

  Scenario: Reject initialization of an already installed agent
    Given a temporary user environment
    And the codex agent is already initialized
    When a user initializes the codex agent again
    Then ZPP reports it as already initialized and directs the caller to sync
    And no integration entry is reprojected

  Scenario: Report an already current integration during synchronization
    Given a temporary user environment
    And the codex agent is already initialized
    When a user synchronizes the codex agent
    Then synchronization reprojects nothing and reports every entry as current

  Scenario: Report a modified owned integration without force
    Given a temporary user environment
    And the codex agent is already initialized
    And one owned workflow skill has drifted from its packaged asset
    When a user synchronizes the codex agent
    Then synchronization reports the modified entry and leaves its content unchanged

  Scenario: Repair a modified owned integration under force
    Given a temporary user environment
    And the codex agent is already initialized
    And one owned workflow skill has drifted from its packaged asset
    When a user synchronizes the codex agent with force
    Then synchronization repairs the modified entry and restores its packaged content

  Scenario: Reproject every owned entry under force
    Given a temporary user environment
    And the codex agent is already initialized
    When a user synchronizes the codex agent with force
    Then synchronization reprojects every owned entry despite no observed drift

  Scenario: Skip an agent that carries no projection during synchronization
    Given a temporary user environment
    When a user synchronizes the codex agent
    Then synchronization reports the agent as uninitialized and projects nothing
