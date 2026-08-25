@workflow-registration
Feature: Keep declared workflow stages visible without rigid execution binding
  Packaged contracts and target-scoped reminder state make the intended sequence
  visible while users retain direct control and standalone components remain usable.

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Strict packaged workflow contracts","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Load a complete contract inventory"}
  Scenario: Load a complete contract inventory
    Given the packaged workflow and component contracts
    When the packaged contract inventory is loaded
    Then every complete playbook and component has one valid cross-referenced contract

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Strict packaged workflow contracts","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reject malformed contract metadata"}
  Scenario: Reject malformed contract metadata
    Given a workflow contract containing an unknown field
    When the malformed workflow contract is decoded
    Then decoding is rejected with the exact source and unknown field

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Start a packaged workflow reminder"}
  Scenario: Start a packaged workflow reminder
    Given an isolated repository with no workflow reminder
    When the zpp-new-feature reminder starts
    Then the persisted checklist reports clarify as its first pending stage

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Resume without resetting progress"}
  Scenario: Resume without resetting progress
    Given an active reminder whose clarify stage is completed
    When the same zpp-new-feature reminder starts again
    Then the completed clarify result remains completed

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve an existing different workflow"}
  Scenario: Preserve an existing different workflow
    Given an active zpp-new-feature reminder
    When zpp-fix-bug is started for the same targets
    Then the existing workflow is reported without replacement

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Require registration only for complete playbooks","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Remind an unregistered playbook to start"}
  Scenario: Remind an unregistered playbook to start
    Given an isolated repository with no workflow reminder
    When the kernel checks a declared playbook component without registration
    Then workflow-start-required is returned without progress

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Require registration only for complete playbooks","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve standalone component use"}
  Scenario: Preserve standalone component use
    Given an isolated repository with no workflow reminder
    When the kernel checks a standalone explore component
    Then the component is allowed and reported as untracked

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Insert a custom reminder stage"}
  Scenario: Insert a custom reminder stage
    Given an active zpp-new-feature reminder
    When a valid custom explore stage is inserted before clarify
    Then status reports the custom stage before clarify

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Upsert a reminder stage idempotently"}
  Scenario: Upsert a reminder stage idempotently
    Given an active zpp-new-feature reminder
    When the same custom stage is upserted twice
    Then exactly one custom stage remains

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reject an invalid checklist edit"}
  Scenario: Reject an invalid checklist edit
    Given an active reminder with an inserted custom explore stage
    When an edit would duplicate the custom stage identifier
    Then the invalid edit is rejected without state change

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Stop reminder state independently of leases"}
  Scenario: Stop reminder state independently of leases
    Given an active zpp-new-feature reminder
    When the active reminder is stopped
    Then workflow status is absent while Bundler state is unchanged

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Return strong non-blocking sequence reminders","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Confirm an in-sequence request"}
  Scenario: Confirm an in-sequence request
    Given an active zpp-new-feature reminder
    When the kernel checks the pending clarify component
    Then the result is an allowed sequence match

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Return strong non-blocking sequence reminders","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Warn about an out-of-sequence request"}
  Scenario: Warn about an out-of-sequence request
    Given an active zpp-new-feature reminder
    When the kernel checks shape-bdd before clarify
    Then the result is an allowed warning naming clarify and all unfinished stages

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Inject compact active workflow status on prompt submission"}
  Scenario: Inject compact active workflow status on prompt submission
    Given an active reminder under a confirmed prompt-submission adapter
    When the prompt reminder hook runs
    Then compact active status is emitted without state change

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Stay silent without an active workflow"}
  Scenario: Stay silent without an active workflow
    Given an adapter with a confirmed prompt-submission context event
    When the prompt reminder hook runs
    Then no prompt text or product state is created

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Omit an unsupported native reminder hook"}
  Scenario: Omit an unsupported native reminder hook
    Given an adapter without a confirmed prompt-submission context event
    When the packaged reminder hook inventory is inspected
    Then no reminder hook is packaged for that adapter

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reconcile the reminder hook through Agent Router"}
  Scenario: Reconcile the reminder hook through Agent Router
    Given an eligible agent integration
    When the project integration is installed
    Then Agent Router owns both zpp-traits and zpp-workflow-reminder

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Record an accepted matching stage"}
  Scenario: Record an accepted matching stage
    Given an active zpp-new-feature reminder
    When the pending clarify result is recorded as completed
    Then shape-bdd becomes the next pending stage

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve progress across processes"}
  Scenario: Preserve progress across processes
    Given an active reminder whose clarify stage is completed
    When a fresh CLI process inspects workflow status
    Then the persisted next stage remains shape-bdd

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Ignore unrelated read-only evidence"}
  Scenario: Ignore unrelated read-only evidence
    Given an active zpp-new-feature reminder
    When read-only exploration is reported while the reminder is active
    Then the clarify stage remains pending

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Keep reminder state separate from lease authority","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Start before governed mutation"}
  Scenario: Start before governed mutation
    Given an isolated repository with no workflow reminder
    When the workflow reminder starts before lease acquisition
    Then no Bundler state exists

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-registration","requirement":"Keep reminder state separate from lease authority","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Associate an observed bundle without changing it"}
  Scenario: Associate an observed bundle without changing it
    Given an active zpp-new-feature reminder
    When an observed bundle is associated with the active reminder
    Then the bundle reference is visible without changing Bundler members
