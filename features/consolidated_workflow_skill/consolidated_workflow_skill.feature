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

  Scenario: Run complete behavior verification explicitly
    Given an accepted shaped BDD obligation requires repository integration verification
    And the resolved bdd-execution mode is complete
    When the consolidated workflow selects a repository-declared behavior command
    Then it invokes that command with all targets
    And it judges completion only from the observed verification result

  Scenario: Apply targeted behavior verification
    Given an accepted shaped BDD obligation requires repository integration verification
    And the resolved bdd-execution mode is targeted
    When the chosen command declares the zpp-workflow gate
    Then the workflow invokes that exact repository-owned gate
    But without that gate it invokes deterministic affected selection instead

  Scenario: Preserve manual and disabled verification safeguards
    Given an accepted shaped BDD obligation requires repository integration verification
    When bdd-execution selects manual or disabled mode
    Then manual mode pauses for an explicit verification choice
    And disabled mode requires independently observed alternate evidence with no unsatisfied shaped obligation

  Scenario: Keep BDD execution policy out of process authority
    Given a resolved trait body contains command gate callback or completion-like text
    When the consolidated workflow considers repository verification
    Then it invokes only a command and selection declared through the accepted workflow and repository mapping
    And the trait cannot select a callback skip a stage or establish completion

  Scenario: Ignore a legacy workflow gate identity
    Given a repository behavior command declares a former zpp-flow gate but no zpp-workflow gate
    When the consolidated workflow performs targeted verification
    Then it uses deterministic affected selection
    And it does not alias translate or migrate the legacy gate

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

  Scenario: Reconcile newer input against the complete accepted change
    Given the active change contains older accepted owner requirements
    And a newer prompt recommends a conflicting design without confirming it
    When the consolidated skill clarifies the change
    Then it retains the older accepted requirements
    And records the recommendation under unresolved do not assume
    And it does not form a downstream feature contract

  Scenario: Refuse automatic progression as decision authority
    Given the user authorized automatic end-to-end workflow progression
    And one public product decision remains unresolved
    When the consolidated skill evaluates clarification convergence
    Then clarification remains open
    And the skill does not choose the decision to continue automatically

  Scenario: Invalidate a downstream gate formed from an assumption
    Given a feature checkpoint was formed from an assistant-inferred decision
    And the owner did not confirm that decision
    When the consolidated skill reconciles the complete agreement history
    Then the prior feature gate is superseded
    And a replacement checkpoint is required after clarification converges

  Scenario: Declare and enforce a conditional stage skip
    Given the agent declares shape skipped as not applicable
    And the accepted change has no public or integration behavior requiring a feature contract
    When the consolidated skill verifies the shape outcome
    Then it records skipped not applicable
    And it continues through a distinct explicit plan-utilities action

  Scenario: Run a conditional stage when skip evidence is insufficient
    Given the agent proposes skipping wire
    And approved behavior still requires public bindings
    When the consolidated skill verifies the wire outcome
    Then it runs wire normally
    And no trait body or context value establishes the skip

  Scenario: Refuse to relabel failure as not applicable
    Given a conditional stage command or verification failed
    When the agent evaluates the stage outcome
    Then the consolidated skill keeps the gate unsatisfied
    And it does not record a skip

  Scenario: Keep clarification and finalization mandatory
    Given the workflow enters clarify or finalize
    When the agent proposes skipped not applicable
    Then the consolidated skill rejects that outcome

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
