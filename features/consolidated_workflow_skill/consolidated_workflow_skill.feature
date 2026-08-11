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

  Scenario: Reauthor the complete applicable reference behavior
    Given the separate reference repository contains the established standard traits
    When ZPP packages its TOML trait source under artifacts traits
    Then related BDD structure BDD TDD build and tool variants are complete flavors
    And focused dependency lease reconciliation and zero-assumption behavior remains represented
    And the packaged source path is not imposed as the runtime collection path

  Scenario: Require an explicit workflow stage
    Given a workflow invocation has repository files stored context and resolved traits
    When the invocation does not identify a stage
    Then the consolidated skill requests the stage
    And it does not infer a stage from those inputs

  Scenario: Apply retained trait bodies without granting authority
    Given an explicit workflow stage resolves several contextual trait bodies
    When the consolidated skill applies those bodies in returned order
    Then the bodies may specialize repository language framework test and build guidance
    But they cannot authorize mutation advance a stage or establish completion

  Scenario: Continue automatically through visible stage actions
    Given the user authorized end-to-end workflow progression
    And the current stage has independently verified completion
    When the workflow continues
    Then it invokes the next stage as a distinct explicit action
    And supplies that stage to trait resolution

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
