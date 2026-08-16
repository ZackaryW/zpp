@openspec-skill-provisioning
Feature: Provision OpenSpec operations at ZPP initialization
  Root initialization freshly supplies the OpenSpec operation skills required by
  the consolidated workflow while reset can discard proven-owned generated skills.

  Scenario: Initialize a complete user workflow integration
    Given the local OpenSpec CLI generates its canonical operation skills
    And a user selects one or more supported agents
    When the user runs zpp init
    Then ZPP validates every selected agent OpenSpec inventory before projection
    And Agent Router installs the workflow skill native hook and six OpenSpec skills for each selected agent
    And each generated skill records the detected OpenSpec version as ZPP provenance

  Scenario: Project every discovered packaged companion skill
    Given ZPP discovers its packaged companion skills from their role directory
    And a user selects one or more supported agents
    When the user runs zpp init
    Then Agent Router projects every discovered companion skill for each selected agent
    And the reported order follows the deterministic packaged order
    And no declared list of companion skill names determines that inventory

  Scenario: Report one lifecycle result per projected asset
    Given a user selects one supported agent
    When the user runs zpp init with JSON output
    Then the ordered report contains one result for the workflow skill and native hook
    And it contains one result for each discovered companion skill
    And it contains one result for each generated OpenSpec skill

  Scenario: Install vendored repository memory guidance
    Given ZPP packages the vendored zmem authoring and query skills as companion skills
    When the user runs zpp init
    Then zmem-author-commits and zmem-query-memory are projected for each selected agent
    And no zmem extension design skill is packaged or projected

  Scenario: Abort initialization before projection on generation failure
    Given the local OpenSpec CLI fails or returns an unexpected inventory for one selected agent
    When the user runs zpp init for several agents
    Then no selected agent workflow hook or skill is projected
    And the generation failure remains visible

  Scenario: Regenerate OpenSpec skills on every initialization
    Given Agent Router owns an earlier generated OpenSpec skill
    And the detected OpenSpec version or generated content changes
    When the user runs zpp init again
    Then ZPP freshly generates every selected agent inventory
    And Agent Router safely reconciles the changed owned skill

  Scenario: Summarize initialization unless JSON is requested
    Given one selected agent has a current complete integration
    When the user runs normal zpp init twice
    Then each default result is one concise line with lifecycle outcome counts
    And an explicit JSON request returns the complete ordered lifecycle report

  Scenario: Force reproject a complete owned integration
    Given one selected agent has a current complete integration
    And one selected skill has diverged under matching Agent Router ownership
    When the user runs zpp init with force
    Then every selected workflow hook authoring and OpenSpec asset is requested for reprojection
    And the owned diverged skill is replaced without adopting unmanaged destinations

  Scenario: Keep grouped workflow lifecycle free of OpenSpec controls
    Given a user selects a supported agent and integration scope
    When the user inspects or invokes workflow install update or remove
    Then only the consolidated workflow skill and native hook are managed
    And no OpenSpec lifecycle option is exposed

  Scenario: Force-delete generated OpenSpec skills during reset
    Given every standard user integration passes complete reset preflight
    And a canonical OpenSpec skill is modified but validly owned by Agent Router
    When a user runs zpp reset with confirmation
    Then Agent Router force-deletes every present canonical OpenSpec skill and ownership record
    And no removed OpenSpec backup or history is retained
    And OpenSpec generation is not invoked

  Scenario: Accept already absent OpenSpec skills during reset
    Given every standard user integration passes complete reset preflight
    And one or more canonical OpenSpec skills and ownership records are absent
    When a user runs zpp reset with confirmation
    Then absent generated skills are treated as converged no-ops
    And OpenLease state is replaced after all removals succeed

  Scenario: Preserve an unmanaged same-named skill during reset
    Given every standard user integration passes complete reset preflight
    And a canonical OpenSpec skill is present without matching Agent Router ownership
    When a user runs zpp reset with confirmation
    Then Agent Router refuses to delete the unmanaged skill
    And reset leaves prior OpenLease state unchanged
