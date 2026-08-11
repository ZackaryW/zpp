@trait-resolution
Feature: Resolve complete trait flavors from explicit context and evidence
  A workflow receives deterministic complete bodies and inspectable context without
  recursive activation or hidden authority.

  Scenario: Select the first direct match in effective source order
    Given a first-win family has matching repository space and global flavors
    When ZPP resolves the family
    Then only the first repository flavor is retained
    And its complete body is returned

  Scenario: Use evidence only as fallback for first-win selection
    Given no flavor directly matches a first-win family
    And the first compatible Flutter flavor has successful workspace evidence
    When ZPP resolves the family
    Then the Flutter flavor is retained
    And later evidence flavors are not considered as winners
    And its missing Flutter facet is backfilled without restarting resolution

  Scenario: Retain all direct and evidence-backed matches
    Given an all family has one direct match and two compatible evidence-backed matches
    When ZPP resolves the family
    Then all three flavors are retained in effective order
    And their complete bodies are returned in that order

  Scenario: Retain only non-dominated extend matches
    Given an extend family has generic Python, Python with uv, and Flutter flavors
    And the known context contains Python Flutter and uv
    When ZPP resolves the family
    Then Python with uv and Flutter are retained in effective order
    And generic Python is removed as dominated

  Scenario: Retain incomparable extend specializations
    Given an extend family matches Python with uv and Python with Click flavors
    When ZPP resolves the family
    Then both complete flavors are retained
    And neither facet constraint set contains the other

  Scenario: Combine distinct evidence-derived values
    Given compatible selected evidence flavors derive Python and Flutter
    And language was not already known
    When ZPP backfills the resolution context
    Then language contains Python followed by Flutter without duplicates
    And resolution does not run again

  Scenario: Preserve higher-authority context
    Given invocation context repository context and stored context provide facet values
    When ZPP builds the known resolution context
    Then invocation values take precedence over repository values
    And repository values take precedence over stored and evidence-derived values
    And a conflicting evidence flavor is excluded

  Scenario: Invalidate stored context that is no longer applicable
    Given ZPP_CONTEXT carries facets provenance target identity and evidence fingerprints
    When its target differs from the selected repository
    Then the stored context is ignored
    When evidence used by a stored value has changed
    Then that evidence-derived value is invalidated

  Scenario: Evaluate the initial observable evidence predicates
    Given a flavor checks a root-anchored workspace path literal file content and uv availability
    When ZPP evaluates its evidence against the selected target
    Then the anchored path cannot match a nested substitute
    And file content is compared literally in the named file
    And the result records has_uv as a boolean

  Scenario: Explain selection without changing it
    Given a resolution contains rejected dominated and evidence-selected flavors
    When a user requests its explanation
    Then the explanation identifies context source order policy decisions and evidence
    And it identifies retained flavors backfilled facets and source provenance
    And the resolved bodies remain unchanged

  Scenario: Leave an unmatched family inactive
    Given no flavor directly matches or has successful compatible evidence
    When ZPP resolves the family
    Then the family contributes no body
