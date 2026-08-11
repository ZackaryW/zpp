@repository-trait-bootstrap
Feature: Use repository traits through bounded component-owned integration
  Repository traits work without registration or space creation while writes and
  external projections remain with their owning components.

  Scenario: Read existing repository traits during an explicit workflow invocation
    Given an unregistered repository contains ZPP context and trait documents
    When a user explicitly invokes the workflow against that repository
    Then ZPP requests read-only invocation-scoped OpenLease bindings for those documents
    And no trust initialization registration topology lease or space is created

  Scenario: Ignore trait files until an invocation targets the repository
    Given a repository contains ZPP trait documents
    When no workflow or trait command targets that repository
    Then ZPP does not open evaluate register or mutate the documents

  Scenario: Fall through without implicitly creating a repository trait
    Given the repository has no bdd trait document
    And space and global bdd contributions are available
    When a user invokes the workflow against the repository
    Then the repository document remains absent
    And the available space and global contributions remain eligible

  Scenario: Initialize only an explicitly requested document
    Given the repository bdd trait document is absent
    When a user runs trait init for bdd against that exact repository
    Then ZPP asks OpenLease to initialize exactly that bounded document
    And no repository registration topology persistent source or space is created

  Scenario: Refuse an implicit repository write
    Given workflow resolution discovers a missing or outdated repository trait document
    When no explicit mutation command was requested
    Then ZPP performs no initialization or managed write

  Scenario: Delegate workflow projection to Agent Router
    Given a user requests the ZPP workflow integration for a supported agent
    When ZPP supplies its consolidated workflow asset
    Then Agent Router owns discovery destination selection installation update and removal
    And ZPP does not write an agent destination directly

  Scenario: Preserve component rejection without a compatibility fallback
    Given OpenLease rejects a document operation or Agent Router rejects a projection
    When ZPP receives that component result
    Then ZPP reports the rejection
    And no ZPP-owned configuration coordination discovery or projection fallback runs

  Scenario: Preserve the established command hierarchy
    Given the ZPP command application is installed
    When a user requests its root and command-group help
    Then init and resolve remain root commands
    And trait init owns exact repository document initialization
    And workflow install update and remove remain grouped commands
    And no flat init-trait install-workflow standalone explain or mirrored space command exists

  Scenario: Preserve explicit multi-agent selection order
    Given a workflow command receives Codex Pi and Codex agent selections in that order
    When ZPP normalizes the Agent Router agent values
    Then Codex and Pi are selected once in first-requested order
    And the workflow operation runs once for each selected agent in that order

  Scenario: Select required agents interactively
    Given a multi-agent command requires selection and has an interactive terminal
    When the user supplies no agent option
    Then ZPP offers Codex Claude Code Pi and Kimi in that order
    And cancelling the selection performs no mutation

  Scenario: Require agents without an interactive terminal
    Given a multi-agent command requires selection without an interactive terminal
    When the user supplies no agent option
    Then ZPP reports that one or more agent values are required
    And no workflow projection is attempted

  Scenario: Restrict resolution to one invoking agent
    Given resolve may use one invoking agent active artifact context
    When the user supplies more than one agent option
    Then ZPP rejects the request without combining their artifact contexts
