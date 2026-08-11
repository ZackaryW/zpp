@consolidated-workflow-skill
Feature: Run the ZPP workflow through one explicit authority
  One distributed workflow skill controls stages and completion while trait bodies
  provide contextual policy without gaining operational authority.

  Scenario: Install one consolidated workflow skill
    Given ZPP is installed for a supported agent
    When Agent Router projects the workflow integration
    Then one consolidated ZPP workflow skill is installed
    And no ZPP 1.x stage skill is required

  Scenario: Keep the workflow definition only in the skill
    Given the packaged workflow skill and trait source are available
    When a user inspects their distributed contents
    Then workflow stages transitions gates and authority exist in the skill
    And no workflow trait family is packaged

  Scenario: Package the reconciled standard behavior collection
    Given ZPP packages its standard TOML traits under artifacts traits
    When a user inspects the packaged family inventory
    Then BDD operation structure and execution remain separate focused families
    And TDD build dependency tooling and zero-assumption behavior remain represented
    And no lease conflict or reconciliation policy family is packaged
    And the packaged source path is not imposed as the runtime collection path

  Scenario: Name BDD execution without creating workflow authority
    Given the packaged BDD execution modes are available
    When a repository resolves its BDD execution policy
    Then manual disabled complete targeted and targeted-default behavior comes from bdd-execution
    And no bdd-workflow compatibility family is packaged

  Scenario: Keep universal and tool guidance precise
    Given the packaged zero-assumptions and tooling families are available
    When a user inspects their activation and flavors
    Then zero-assumptions declares always-run activation
    And tooling contains evidence-backed rg and jq guidance without zmem workflow policy

  Scenario: Keep component operations with their owners
    Given a workflow encounters an OpenLease conflict or final reconciliation
    When ZPP determines the governing behavior
    Then OpenLease or the consolidated workflow skill supplies the operational contract
    And no packaged trait is treated as lease or reconciliation authority

  Scenario: Require an explicit workflow stage
    Given a workflow invocation has repository files stored context and resolved traits
    When the invocation does not identify a stage
    Then the consolidated skill requests the stage
    And it does not infer a stage from those inputs

  Scenario: Apply automatically injected trait bodies without granting authority
    Given the native ZPP hook injected several complete contextual trait bodies
    When the consolidated skill applies those bodies in injected order
    Then the bodies may specialize repository language framework test and build guidance
    But they cannot authorize mutation advance a stage or establish completion

  Scenario: Keep trait bootstrap out of the workflow skill
    Given the packaged consolidated workflow skill is available
    When a user inspects its workflow instructions
    Then the skill does not instruct the agent to run trait resolution
    And the skill does not instruct the agent to publish ZPP_CONTEXT

  Scenario: Continue automatically through visible stage actions
    Given the user authorized end-to-end workflow progression
    And the current stage has independently verified completion
    When the workflow continues
    Then it invokes the next stage as a distinct explicit action
    And it does not delegate stage choice to the trait hook

  Scenario: Delegate operations to their owning components
    Given a workflow stage requires OpenSpec OpenLease and Agent Router operations
    When the consolidated skill dispatches those operations
    Then it follows the installed skill that owns each OpenSpec operation
    And uses OpenLease only for its public coordination and configuration contracts
    And uses Agent Router only for its public discovery and projection contracts

  Scenario: Ignore legacy stage skills
    Given a machine retains one or more ZPP 1.x workflow skills
    When ZPP 2.0 runs its workflow
    Then it does not invoke translate or treat them as migration sources
