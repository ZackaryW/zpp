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
    And it does not initialize the bundler child

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
    Then every current packaged integration entry is installed

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

  # zpp-spec: {"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Ownership-safe obsolete workflow retirement","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Retire an owned obsolete workflow projection during synchronization"}
  Scenario: Retire an owned obsolete workflow projection during synchronization
    Given a temporary user environment
    And the codex agent is already initialized
    And an obsolete workflow skill is owned by Agent Router
    When a user synchronizes the codex agent
    Then synchronization removes the owned obsolete workflow skill
    And the current packaged inventory remains installed

  # zpp-spec: {"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Ownership-safe obsolete workflow retirement","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Preserve an unowned obsolete OpenSpec identity during synchronization"}
  Scenario: Preserve an unowned obsolete OpenSpec identity during synchronization
    Given a temporary user environment
    And the codex agent is already initialized
    And an unowned obsolete OpenSpec identity exists
    When a user synchronizes the codex agent
    Then synchronization reports the obsolete identity as preserved
    And the unowned obsolete identity remains unchanged

  # zpp-spec: {"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation during initialization"}
  Scenario: Migrate an owned old-only user installation during initialization
    Given a temporary user environment
    And only an owned obsolete workflow skill is installed
    When a user initializes the codex agent
    Then every current packaged integration entry is installed
    And the owned obsolete workflow skill is retired after current verification
    And initialization identifies the old-only migration as complete

  # zpp-spec: {"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Block initialization on an unowned obsolete collision"}
  Scenario: Block initialization on an unowned obsolete collision
    Given a temporary user environment
    And an unowned obsolete OpenSpec identity exists
    When a user initializes the codex agent
    Then initialization reports an obsolete migration conflict
    And no current packaged integration entry is projected
    And the unowned obsolete identity remains unchanged

  # zpp-spec: {"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Explicit scope-aware lifecycle migration","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation"}
  Scenario: Migrate an owned old-only user installation
    Given a temporary user environment
    And only an owned obsolete workflow skill is installed
    When a user synchronizes the codex agent
    Then every current packaged integration entry is installed
    And the owned obsolete workflow skill is retired after current verification
    And synchronization identifies the old-only migration as complete

  Scenario: Create home state on first automatic lease acquisition
    Given a temporary user environment
    And a disposable Git worktree and an absent ZPP home
    When ZPP automatically acquires a store change bundle
    Then the selected home and its bundler child exist
    And no legacy OpenLease state is created or changed
