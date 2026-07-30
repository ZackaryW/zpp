Feature: Bootstrap ZPP and configure agent applications
  ZPP users can initialize neutral global state and opt into thin agent integrations
  without modifying projects or leaking trait policy into agent setup.

  Scenario: ZPP reports its identity and initial command surface
    Given ZPP is installed
    When the user requests the ZPP version
    And the user requests ZPP help
    Then the product identifies itself as ZPP version 0.9.0
    And the help exposes the confirmed initial command surface
    And the help does not expose a separate agent installation command

  Scenario: First noninteractive initialization creates only neutral user state
    Given a clean user home
    And a project without local ZPP state
    And no interactive terminal is available
    When the user runs zpp init
    Then initialization succeeds
    And the neutral global trait layer exists
    And the empty profile, saved, and cache roots exist
    And no named profile exists
    And no cache artifact exists
    And the project still has no local ZPP state
    And no agent application is configured

  Scenario: Initialization completes missing state without rewriting valid state
    Given partially initialized valid user state with missing required entries
    And the existing managed files have distinguishable valid formatting
    And no interactive terminal is available
    When the user runs zpp init twice
    Then initialization succeeds both times
    And every missing required user-state entry is created
    And every pre-existing managed file is byte-for-byte unchanged
    And the second initialization makes no further change

  Scenario: Invalid managed user state blocks all bootstrap writes
    Given user state contains an invalid managed source
    And other required user-state entries are missing
    And no interactive terminal is available
    When the user runs zpp init
    Then initialization fails as a managed-state rejection
    And the diagnostic identifies the invalid source path
    And no missing user-state entry is created
    And the existing user state is unchanged

  Scenario: Repeated explicit agent options configure exactly those agents
    Given a clean user home
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user runs zpp init with agents Pi and Codex
    Then initialization succeeds without offering agent selection
    And Pi has one thin ZPP instruction integration and one ZPP-managed skill
    And Codex has one thin ZPP instruction integration and one ZPP-managed skill
    And Claude Code is unchanged

  Scenario: Interactive initialization offers agent selection for an existing root
    Given valid initialized user state
    And an interactive terminal is available
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user runs zpp init and selects Claude Code
    Then one selector offers Pi, Codex, and Claude Code
    And Claude Code has one thin ZPP instruction integration and one ZPP-managed skill
    And the existing user state is unchanged
    And Pi and Codex are unchanged

  Scenario: Reconfiguring an agent is idempotent and does not leak policy
    Given valid initialized user state contains an activatable authored trait
    And no trait cache exists
    And Pi has a ZPP integration surrounded by unmanaged content
    And Codex was previously configured by ZPP
    When the user runs zpp init with agent Pi twice
    Then both initializations succeed without offering agent selection
    And Pi has exactly one valid ZPP integration
    And Pi's unmanaged content is byte-for-byte unchanged
    And Codex remains installed and unchanged
    And no effective trait, workflow direction, or platform guidance is copied into Pi
    And no trait cache is created
    And trait resolution is not invoked

  Scenario: An unmanaged adapter conflict is rejected without overwrite
    Given a clean user home
    And Claude Code has an unmanaged skill conflicting with ZPP integration
    When the user runs zpp init with agent Claude Code
    Then the neutral global user state is initialized
    And agent setup fails as a managed-state rejection
    And the diagnostic identifies the conflicting path
    And the conflicting unmanaged skill is unchanged
    And all other Claude Code content is unchanged

  Scenario: Unsupported agent names are usage errors
    Given a clean user home
    When the user runs zpp init with an unsupported agent name
    Then the invocation fails as a usage error
    And no ZPP user state is created
    And no agent application is changed
