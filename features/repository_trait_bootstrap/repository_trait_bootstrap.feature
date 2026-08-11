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
    When a user explicitly requests its initialization
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
