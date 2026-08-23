@repository-trait-bootstrap
Feature: Bootstrap repository traits only when explicitly requested
  ZPP reads repository trait documents that already exist and creates one only
  when a caller names it, never as a side effect of resolution. Agent selection
  and the public command hierarchy stay explicit.

  Scenario: Initialize only an explicitly requested document
    Given a disposable repository
    When a caller explicitly initializes the repository context and a bdd trait
    Then exactly the context document and that trait document exist
    And the bound repository source exposes only the bdd family

  Scenario: Preserve the established command hierarchy
    Given the public command help is available
    Then every established root command is exposed
    And the grouped workflow exposes install update and remove
    And the minimal lease bridge is exposed
    And no workspace or legacy install-workflow command is exposed

  Scenario: Preserve explicit multi-agent selection order
    Given an explicit agent selection repeating one agent
    Then the normalized selection keeps first-seen order without duplicates

  Scenario: Select required agents interactively
    Given no agent is supplied and the terminal is interactive
    When the caller cancels the selection prompt
    Then the selection reports cancellation rather than choosing an agent

  Scenario: Require agents without an interactive terminal
    Given no agent is supplied and no interactive terminal is available
    Then the selection is rejected rather than defaulting to every agent

  Scenario: Restrict resolution to one invoking agent
    Given several invoking agents are supplied where one is required
    Then the selection is rejected

  Scenario: Run direct repository behavior without lease state
    Given a disposable repository with a committed base
    When the caller initializes repository behavior verification
    Then a repository behavior mapping exists
    And no session claim permit or lease is created

  Scenario: Resolve repository traits without lease state
    Given a disposable repository with repository trait documents
    When the caller resolves that repository's traits
    Then the bounded repository context resolves
    And no session claim permit or lease is created

  Scenario: Bind the invoking agent router to the repository
    Given a disposable repository
    When the caller builds the codex agent router for that repository
    Then the router resolves the user home and that repository as its project root
