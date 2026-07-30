Feature: Initialize global ZPP state
  ZPP users can establish the default global trait layer without modifying a project.

  Scenario: First initialization creates only user-owned global state
    Given a clean user home and a project without local ZPP state
    When the user runs zpp init
    Then initialization succeeds
    And the global trait trigger configuration exists
    And the project still has no local ZPP state
