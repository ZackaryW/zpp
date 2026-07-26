Feature: Reference store assignment refuses rather than guesses
  A workset may draw on registered stores as read-only knowledge corpora.
  An assignment must name something openspec can actually resolve, so both
  an unresolvable registry and an unknown assignment are refusals, never
  silent writes.

  Scenario: Assignment fails closed when the registry cannot be consulted
    Given a workset "demo" with member "project"
    When the owner assigns reference store "ghost-store" to workset "demo"
    Then the command fails
    And workset "demo" has no reference stores

  Scenario: Unassigning a store that was never assigned is refused
    Given a workset "demo" with member "project"
    When the owner unassigns reference store "ghost-store" from workset "demo"
    Then the command fails
    And the error output contains "not assigned"
