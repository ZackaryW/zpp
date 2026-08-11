## ADDED Requirements

### Requirement: Family activation before selection
For unfiltered resolution, ZPP SHALL use normal facet and evidence candidate formation for an `automatic` family, exclude a `manual` family, and treat every effective flavor of an `always-run` family as an activation candidate without evaluating its facets or evidence. ZPP SHALL then apply the effective family's declared selection policy to the resulting candidates. Facets of bypass-selected always-run flavors SHALL NOT be treated as evidence-derived backfill.

#### Scenario: Exclude a manual family from common resolution
- **WHEN** unfiltered resolution encounters a manual family whose evidence would otherwise match
- **THEN** the family contributes no candidate and no body

#### Scenario: Select an always-run family without activation evidence
- **WHEN** unfiltered resolution encounters an always-run family with no matching known facets or workspace evidence
- **THEN** every effective flavor enters policy selection and the retained complete bodies are returned

#### Scenario: Preserve extend policy for always-run
- **WHEN** an always-run extend family contains generic Python, Python-and-uv, and Flutter flavors
- **THEN** selection removes generic Python as dominated and retains Python-and-uv and Flutter in effective order

### Requirement: Direct trait-family query
`resolve` SHALL accept repeatable `--trait <family>` filters and SHALL limit one filtered resolution to exactly the distinct named families in first-requested order. A named manual or automatic family SHALL use normal facet and evidence activation; a named always-run family SHALL retain always-run activation. Requesting an unknown family SHALL fail visibly without returning unrelated always-run families.

#### Scenario: Query a manual family directly
- **WHEN** a caller names a manual family whose flavor matches the current facets or evidence
- **THEN** resolution returns that family's normally selected complete bodies

#### Scenario: Manual query does not force a flavor
- **WHEN** a caller names a manual family but none of its flavors matches normal facets or evidence
- **THEN** the requested family returns no body

#### Scenario: Query several families once each
- **WHEN** a caller repeats `--trait` with a duplicate family name
- **THEN** resolution considers each distinct requested family once in first-requested order

#### Scenario: Reject an unknown family
- **WHEN** a caller names a family absent from the effective catalog
- **THEN** resolution fails visibly and returns no unrelated always-run output

### Requirement: Prompt-ready and diagnostic rendering
Successful `resolve` without `--explain` SHALL render only every retained complete body in deterministic requested-family and effective-selection order, with an unambiguous separator between bodies and no JSON transport envelope. An empty successful resolution SHALL emit no trait body content. `resolve --explain` SHALL emit a structured diagnostic result containing the same selected bodies, effective context including the recomputed `ZPP_CONTEXT`, and deterministic selection decisions.

#### Scenario: Inject default resolver output
- **WHEN** automatic resolution retains several complete bodies
- **THEN** default stdout contains those bodies in deterministic order without diagnostic metadata

#### Scenario: Explain the same resolution
- **WHEN** the same invocation adds `--explain`
- **THEN** structured output reports the same bodies and the context and decisions that produced them

#### Scenario: Resolve no active body
- **WHEN** successful unfiltered resolution retains no automatic or always-run body
- **THEN** default stdout contributes no trait content
