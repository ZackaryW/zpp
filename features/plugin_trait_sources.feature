Feature: Resolve traits from active agent plugins
  ZPP users can consume validated plugin-authored traits in place while keeping
  user-owned layers authoritative and inactive editor material excluded.

  Scenario Outline: Resolution discovers only the invoking agent's active plugins
    Given <agent> reports one active plugin with a valid trait source
    And the other supported agents report different active plugins
    And <agent> also contains available, disabled, orphaned, and stale plugin material
    When the user runs zpp resolve --agent <agent> for the target
    Then only <agent>'s active plugin trait source participates before global
    And no other agent or inactive plugin material participates

    Examples:
      | agent  |
      | codex  |
      | claude |
      | pi     |

  Scenario: Direct resolution preserves ZPP-only behavior
    Given every supported agent reports an active plugin trait source
    When the user runs zpp resolve for the target without --agent
    Then no editor plugin trait source participates
    And global, selected profile, saved, and repository layers retain their established order

  Scenario: Plugin triggers and later user activation compose without copying
    Given an active plugin root contains trait.json and valid Markdown trait definitions
    And its trait.json conditionally activates one definition
    And another plugin definition is omitted from its trigger list
    And a later repository layer activates and configures the omitted definition
    When the user runs zpp resolve with that plugin's agent identity
    Then the plugin trigger participates before global
    And the repository activation uses the discovered omitted definition
    And later replacement, configuration, and trigger-overwrite behavior remains authoritative
    And the plugin source is byte-for-byte unchanged
    And no plugin trait is copied into a user-owned profile

  Scenario: Active plugin updates and removal cannot leave stale traits
    Given one active plugin source has already produced independently cached traits
    When the invoking agent replaces that plugin with a new active version and root
    Then subsequent resolution uses only the new active source
    When the invoking agent disables or uninstalls the plugin
    Then subsequent resolution excludes that source even while former files or cache state remain

  Scenario: External definitions are deterministic and conflict-safe
    Given active plugin sources are presented in arbitrary discovery order
    When ZPP composes their declared trait sources
    Then sources are ordered by stable plugin identity
    And byte-identical definitions with the same trait name participate once
    And their valid triggers remain eligible through ordinary activation
    But different content for the same trait name fails complete resolution
    And the diagnostic identifies every conflicting plugin source
    And stdout contains no stale, partial, or fallback trait context

  Scenario: A malformed declared plugin source fails completely
    Given an active plugin declares trait.json and traits but one authored document is invalid
    When the user runs zpp resolve with that plugin's agent identity
    Then resolution fails with a source-oriented diagnostic
    And stdout is empty
    And no stale or partial trait context is returned
