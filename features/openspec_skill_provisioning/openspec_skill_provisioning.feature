@openspec-skill-provisioning
Feature: Project the packaged ZPP workflow family
  ZPP projects its complete packaged workflow family without generating or
  installing upstream OpenSpec skills. OpenSpec is consulted only by a bounded
  adapter when that operation is invoked.

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Canonical packaged ZPP workflow skill set","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Prepare the exact packaged workflow inventory"}
  Scenario: Prepare the exact packaged workflow inventory
    When ZPP prepares its packaged workflow family
    Then all current workflow entries, stages, adapters, and repository verifier are present
    And onboarding and removed workflow identities are absent

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Initialization and synchronization own packaged projection","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Initialize the current user integration"}
  Scenario: Initialize the current user integration
    Given a disposable user home
    When a user initializes the codex agent
    Then one lifecycle result is reported per current packaged asset
    And every current packaged skill is present on disk
    And no generated OpenSpec skill or provenance is present

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Lifecycle independence and runtime OpenSpec compatibility","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Reconcile lifecycle without invoking OpenSpec"}
  Scenario: Reconcile lifecycle without invoking OpenSpec
    Given a disposable user home
    When a user initializes synchronizes and resets the codex integration
    Then every lifecycle command succeeds without an OpenSpec process

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Initialization and synchronization own packaged projection","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Report a complete packaged integration as current"}
  Scenario: Report a complete packaged integration as current
    Given a disposable user home
    And the codex agent is initialized
    When a user synchronizes the codex agent
    Then every current packaged asset reports current

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"ZPP-only tool distribution boundary","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Install the built ZPP distribution as the only tool"}
  Scenario: Install the built ZPP distribution as the only tool
    Given a disposable uv tool environment
    When a user installs the built ZPP wheel as a tool
    Then zpp is the only installed tool command
    And the distribution module and CLI versions agree
    And OpenSpec Bundler is present only as a ZPP dependency
