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

  Scenario: Enrich context before final family selection
    Given no language is known and Cucumber workspace evidence identifies TypeScript
    And another family has a TypeScript flavor without its own evidence
    When ZPP resolves all active families
    Then language is derived before final family selection
    And both TypeScript complete bodies are returned in the same resolution
    And a facet-only match does not start another enrichment pass

  Scenario: Extend list-valued context with distinct evidence
    Given repository language context contains Python followed by Rust
    And compatible evidence derives Python and TypeScript
    When ZPP enriches the resolution context
    Then language contains Python Rust and TypeScript once each in that order
    And each evidence-derived member retains its own provenance

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

  Scenario: Invalidate only one evidence-derived list member
    Given stored language context contains authored Python and evidence-derived TypeScript
    When only the TypeScript evidence fingerprint changes
    Then TypeScript is removed from stored language context
    And authored Python remains available

  Scenario: Upgrade prior stored context representation
    Given a valid version one ZPP_CONTEXT value
    When ZPP restores and completes the context
    Then compatible values remain available
    And the returned context uses member-level provenance

  Scenario: Protect explicit workflow stage context
    Given repository and stored context attempt to provide workflow stages
    When an invocation explicitly requests the shape stage
    Then only the validated explicit stage participates in matching
    And the protected stage is not persisted as descriptive context

  Scenario: Reject an unknown explicit workflow stage
    Given an invocation names a stage outside the consolidated workflow
    When ZPP builds its resolution context
    Then resolution fails visibly

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

  Scenario: Exclude manual families from common resolution
    Given a manual family has a flavor with successful activation evidence
    When ZPP resolves all commonly active families
    Then the manual family contributes no body

  Scenario: Query a manual family with normal activation
    Given a manual family has one matching flavor and one unmatched flavor
    When a user resolves that family directly
    Then only the normally selected matching flavor contributes its complete body
    And unrelated always-run families do not contribute

  Scenario: Return no forced body for an unmatched manual query
    Given a manual family has no matching facet or evidence flavor
    When a user resolves that family directly
    Then the requested family contributes no body

  Scenario: Resolve repeated named families in first-requested order
    Given several known trait families are available
    When a user requests two families and repeats the first family
    Then each requested family is considered once in first-requested order

  Scenario: Reject an unknown named family
    Given an always-run family is available
    When a user directly requests an unknown family
    Then resolution fails visibly
    And the unrelated always-run family contributes no body

  Scenario: Apply selection after always-run activation bypass
    Given an always-run extend family has generic Python Python with uv and Flutter flavors
    And no flavor has matching context or evidence
    When ZPP resolves all commonly active families
    Then Python with uv and Flutter are retained in effective order
    And generic Python is removed as dominated
    And bypass-selected facets do not backfill the context

  Scenario: Render complete bodies for prompt injection by default
    Given resolution retains several complete trait bodies
    When a user resolves without explanation
    Then standard output contains only those complete bodies in deterministic order
    And no diagnostic envelope is emitted

  Scenario: Render structured diagnostics only when requested
    Given resolution retains several complete trait bodies and recomputes stored context
    When a user resolves with explanation
    Then structured output contains the same bodies effective context and deterministic decisions
