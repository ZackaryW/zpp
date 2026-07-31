Feature: Bootstrap ZPP and configure agent applications
  ZPP users can initialize neutral global state, a reusable default profile, and
  optional native lifecycle hooks without modifying projects or leaking trait
  policy into agent setup.

  Scenario: ZPP reports its identity and initial command surface
    Given ZPP is installed
    When the user requests the ZPP version
    And the user requests ZPP help
    Then the product identifies itself as ZPP version 0.9.0
    And the help exposes the confirmed initial command surface
    And the help exposes the independent workflow lifecycle command group
    And the help does not expose a generic skill command group

  Scenario: First noninteractive initialization creates required user state
    Given a clean user home
    And a project without local ZPP state
    And no interactive terminal is available
    When the user runs zpp init
    Then initialization succeeds
    And the neutral global trait layer exists
    And the persistent user-owned default profile exists
    And the default profile activates exactly automatic-workflow, zero-assumptions, and ponytail
    And the default profile contains inactive python-bdd, python-tdd, and python-build traits
    And the saved and cache roots exist
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

  Scenario: Initialization preserves a user-edited default profile
    Given valid initialized user state
    And the default profile has valid user-authored changes with distinctive formatting
    And no interactive terminal is available
    When the user runs zpp init
    Then initialization succeeds
    And the complete default profile is byte-for-byte unchanged
    And no bundled default content is reapplied

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
    And the current project has no repository-local agent integration
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user runs zpp init with agents Pi and Codex
    Then initialization succeeds without offering agent selection
    And Pi has one ZPP-managed native lifecycle hook
    And Codex has one ZPP-managed native lifecycle hook
    And neither agent receives a ZPP instruction paragraph or skill
    And their agent-owned hook trust and enablement state is unchanged
    And Claude Code is unchanged
    And the current project still has no repository-local agent integration

  Scenario: Interactive initialization offers agent selection for an existing root
    Given valid initialized user state
    And an interactive terminal is available
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user runs zpp init and selects Claude Code
    Then one selector offers Pi, Codex, and Claude Code
    And Claude Code has one ZPP-managed native lifecycle hook
    And Claude Code receives no ZPP instruction paragraph or skill
    And the existing user state is unchanged
    And Pi and Codex are unchanged

  Scenario: Submitting an empty interactive selection configures no agent
    Given valid initialized user state
    And an interactive terminal is available
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user runs zpp init and submits the selector with no checked agent
    Then initialization succeeds
    And no agent application is changed
    And the existing user state is unchanged

  Scenario: Cancelling interactive selection is distinct from submitting no agents
    Given valid initialized user state
    And an interactive terminal is available
    And Pi, Codex, and Claude Code have no ZPP integration
    When the user cancels zpp init from the agent selector
    Then initialization is cancelled
    And no agent application is changed
    And the existing user state is unchanged

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
    And no effective trait, workflow direction, or platform guidance is copied into Pi's installed hook
    And no trait cache is created
    And trait resolution is not invoked

  Scenario Outline: A native agent hook resolves and injects current traits
    Given <agent> was configured by ZPP
    And its native hook is trusted and enabled by the agent application
    And its current working directory resolves one effective trait document
    When <lifecycle> invokes the ZPP hook
    Then ZPP resolves the current working directory
    And the complete effective trait document is injected exactly once into <agent> context

    Examples:
      | agent       | lifecycle                                         |
      | Pi          | before_agent_start                                |
      | Codex       | SessionStart for startup, resume, clear, or compact |
      | Claude Code | SessionStart for startup, resume, clear, compact, or fork |

  Scenario Outline: A native agent hook injects nothing for empty resolution
    Given <agent> was configured by ZPP
    And its native hook is trusted and enabled by the agent application
    And its current working directory resolves no active traits
    When the native ZPP hook is invoked
    Then hook execution succeeds
    And no ZPP trait context is injected into <agent>

    Examples:
      | agent       |
      | Pi          |
      | Codex       |
      | Claude Code |

  Scenario Outline: A native agent hook never injects stale context after failure
    Given <agent> was configured by ZPP
    And its native hook is trusted and enabled by the agent application
    And its current working directory causes trait resolution to fail
    When the native ZPP hook is invoked
    Then the resolution failure is surfaced through <agent>
    And no stale or partial ZPP trait context is injected

    Examples:
      | agent       |
      | Pi          |
      | Codex       |
      | Claude Code |

  Scenario: An unmanaged adapter conflict is rejected without overwrite
    Given a clean user home
    And Claude Code has an unmanaged hook conflicting with ZPP integration
    When the user runs zpp init with agent Claude Code
    Then the neutral global user state is initialized
    And agent setup fails as a managed-state rejection
    And the diagnostic identifies the conflicting path
    And the conflicting unmanaged hook is unchanged
    And all other Claude Code content is unchanged

  Scenario: Every selected agent is preflighted before any agent changes
    Given a clean user home
    And Pi has no ZPP integration
    And Codex has an unmanaged hook conflicting with ZPP integration
    When the user runs zpp init with agents Pi and Codex
    Then the neutral global user state is initialized
    And agent setup fails as a managed-state rejection
    And Pi remains unchanged
    And the conflicting Codex hook remains unchanged

  Scenario: Unsupported agent names are usage errors
    Given a clean user home
    When the user runs zpp init with an unsupported agent name
    Then the invocation fails as a usage error
    And no ZPP user state is created
    And no agent application is changed
