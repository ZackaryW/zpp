@openspec-skill-provisioning
Feature: Provision OpenSpec operation skills with the ZPP integration
  Root initialization generates the OpenSpec operation skills an agent needs and
  projects them alongside the packaged workflow and companion skills, so a
  workflow can begin without a separate setup step.

  Scenario: Package the discovered companion inventory
    Given the packaged companion inventory is loaded
    Then it contains the vendored zmem authoring and query skills
    And it contains no workspace-management skill
    And it contains no withdrawn zmem extension skill

  Scenario: Keep OpenSpec controls out of the grouped workflow lifecycle
    Given the grouped workflow lifecycle help is available
    Then no grouped workflow operation exposes an OpenSpec control

  Scenario: Initialize a complete user workflow integration
    Given a disposable user home
    When a user initializes the codex agent
    Then one lifecycle result is reported per projected asset
    And every packaged companion skill is present on disk
    And each generated OpenSpec skill records ZPP as its generator

  Scenario: Report a complete integration as current
    Given a disposable user home
    And the codex agent is initialized
    When a user synchronizes the codex agent
    Then every projected asset reports current

  Scenario: Repair a modified generated OpenSpec skill under force
    Given a disposable user home
    And the codex agent is initialized
    And a generated OpenSpec skill has been modified locally
    When a user synchronizes the codex agent with force
    Then the generated OpenSpec skill content is restored

  Scenario: Force-delete generated OpenSpec skills during reset
    Given a disposable user home
    And the codex agent is initialized
    And a generated OpenSpec skill has been modified locally
    When a user confirms a complete reset
    Then the generated OpenSpec skill is removed
    And managed Bundler state is replaced

  Scenario: Preserve an unmanaged same-named skill
    Given a disposable user home
    And an unmanaged workflow skill occupies the codex surface
    When a user initializes the codex agent
    Then ZPP reports the agent as already initialized
    And forced synchronization preserves that unmanaged skill
