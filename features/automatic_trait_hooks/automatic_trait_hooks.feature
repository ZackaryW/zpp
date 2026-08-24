@automatic-trait-hooks
Feature: Inject repository traits through agent-native hooks
  Each supported agent receives environment policy automatically while the
  workflow family retains ZPP workflow authority. Injection semantics
  and failure isolation are canonical requirements of the native hook contract,
  verified by inspection rather than by scenarios.

  Scenario Outline: Package the native hook for each supported agent
    Given ZPP packages the <agent> workflow integration
    When the packaged native hook is inspected
    Then the hook declares the <format> native format
    And the hook is compatible with only that agent
    And the hook resolves the current repository with <agent> as the invoking agent

    Examples:
      | agent  | format  |
      | codex  | json    |
      | claude | json    |
      | kimi   | toml    |
      | pi     | pi-file |

  Scenario: Keep guard and prompt events out of the packaged hook
    Given ZPP packages the codex workflow integration
    When the packaged native hook is inspected
    Then the hook declares no guard and no prompt-submit event

  # zpp-spec: {"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Install the complete workflow family and trait hook together"}
  Scenario: Install the complete workflow family and trait hook together
    Given a disposable project root
    When a user installs the codex workflow integration into that project
    Then Agent Router projects the complete packaged workflow family and zpp-traits in deterministic order

  # zpp-spec: {"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Remove the complete workflow family and trait hook together"}
  Scenario: Remove the complete workflow family and trait hook together
    Given a disposable project root
    And the codex workflow integration is installed into that project
    When a user removes that workflow integration
    Then Agent Router removes the complete packaged workflow family and zpp-traits in deterministic order

  # zpp-spec: {"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Update an owned old-only project workflow in place"}
  Scenario: Update an owned old-only project workflow in place
    Given a disposable project root
    And only an owned obsolete workflow skill is installed into that project
    When a user updates the codex workflow integration in that project
    Then the complete current workflow integration replaces the obsolete project skill

  # zpp-spec: {"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Ownership-safe former hook migration","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Update an intact former Codex hook identity in place"}
  Scenario: Update an intact former Codex hook identity in place
    Given a disposable project root
    And the codex workflow integration carries intact former hook ownership
    When a user updates the codex workflow integration in that project
    Then current project hook ownership replaces the former identity

  # zpp-spec: {"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Refuse a conflicting workflow installation before mutation"}
  Scenario: Refuse a conflicting workflow installation before mutation
    Given a disposable project root
    And an unmanaged current workflow destination exists in that project
    When a user installs the codex workflow integration into that project
    Then installation reports the exact conflict without projecting another family member

  Scenario: Resolve traits from a native hook without coordination state
    Given a disposable repository with no Bundler lease state
    When the packaged hook resolution runs against that repository
    Then the repository traits resolve
    And no session or Bundler lease state is created

  Scenario: Package the hard-cut trait hook identity
    Given ZPP packages the codex workflow integration
    When the packaged native hook is inspected
    Then the hook identity is zpp-traits
    And no zpp-session compatibility hook is packaged
