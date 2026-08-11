## MODIFIED Requirements

### Requirement: Non-recursive facet backfill
Before final family selection, ZPP SHALL form one deterministic evidence-enrichment pass from compatible flavors with successful declared `when` branches. A `first-win` family SHALL contribute only its first compatible successful evidence fallback when no flavor directly matches the base context; an `all` or `extend` family SHALL contribute every compatible successful evidence candidate. Each contributing flavor SHALL add its declared facets that are eligible for enrichment, and typed evidence predicates SHALL add their derived runtime facts. ZPP SHALL use the enriched context for final selection across every family during the same resolution.

Equal contributions SHALL be deduplicated. Distinct contributions to a missing descriptive facet SHALL become an ordered list following effective family and flavor order. An existing repository list or evidence-owned scalar or list SHALL append distinct evidence-derived values in that order. An explicit invocation value and an authoritative repository scalar SHALL NOT be overwritten or expanded by evidence. A flavor selected only because enrichment made its facets match SHALL NOT cause another enrichment pass. Protected workflow runtime controls SHALL NOT be authored by evidence enrichment.

#### Scenario: Derive a language before final family selection
- **WHEN** no language is known, a Cucumber workspace predicate succeeds for a flavor declaring TypeScript, and another family has a TypeScript flavor
- **THEN** ZPP adds `language = "typescript"` before final selection and returns both applicable complete bodies in the same resolution

#### Scenario: Preserve known explicit context
- **WHEN** evidence contributes a value that conflicts with an explicitly supplied invocation facet
- **THEN** ZPP preserves the explicit value and does not add the evidence value

#### Scenario: Extend a repository language list uniquely
- **WHEN** repository context declares Python and Rust while successful evidence contributes Python and TypeScript
- **THEN** enriched context contains Python, Rust, and TypeScript once each in that order

#### Scenario: Avoid recursive facet derivation
- **WHEN** evidence derives TypeScript and that value directly activates a facet-only TypeScript flavor without evidence
- **THEN** ZPP may select that flavor's body but does not publish context merely because final selection retained it

### Requirement: Stored backfilled session context
ZPP SHALL serialize updated stored descriptive context as one compact JSON `ZPP_CONTEXT` value that a supported session integration can publish for later invocations. The complete value SHALL include facet values, member-level value provenance, selected target identity, and relevant evidence fingerprints. Publication SHALL replace the prior complete value. A target mismatch SHALL invalidate the stored context. Changed evidence SHALL remove only affected evidence-derived members and SHALL remove a facet only when no members remain. ZPP SHALL accept the prior version-1 key-level representation and emit the current representation after successful resolution. Stored values SHALL NOT grant mutation, stage-transition, stage-outcome, or completion authority.

#### Scenario: Carry detected language into a later invocation
- **WHEN** evidence enrichment derives the TypeScript facet and the session integration publishes the returned context
- **THEN** a later compatible invocation can receive TypeScript as stored descriptive context without treating it as workflow authority

#### Scenario: Ignore context from another target
- **WHEN** `ZPP_CONTEXT` identifies a repository target different from the current selected target
- **THEN** resolution ignores that stored context instead of applying its facets

#### Scenario: Invalidate one changed list member
- **WHEN** stored language context contains authored Python and evidence-derived TypeScript and only the TypeScript evidence changes
- **THEN** ZPP removes TypeScript while preserving Python

#### Scenario: Upgrade prior stored context
- **WHEN** ZPP restores a valid version-1 context value and completes resolution
- **THEN** it preserves compatible values and emits them using the current member-level representation

### Requirement: Repository and environment context inputs
Resolution SHALL accept repository-known scalar or multi-value string facets from the `[facet]` table in `.zpp/zpp.toml`, an explicitly supplied workflow stage, compatible stored descriptive context from a ZPP-owned session value, and explicit invocation facets. Explicit invocation context SHALL take precedence over repository context, and both SHALL take precedence over stored and evidence-derived context. Reserved workflow runtime controls SHALL be accepted only from explicit invocation inputs, SHALL be validated against their supported value set, and SHALL NOT be restored from descriptive stored context or authored by repository context.

#### Scenario: Resolve with repository-known facets
- **WHEN** `.zpp/zpp.toml` declares Python and Click facets and the workflow explicitly requests the shape stage
- **THEN** resolution uses those exact descriptive values and the explicit protected stage during matching

#### Scenario: Preserve explicit stage authority
- **WHEN** repository or stored context attempts to provide a stage different from the explicitly requested workflow action
- **THEN** ZPP rejects or ignores the non-invocation control and uses the explicit action's validated stage

#### Scenario: Reject an unknown stage
- **WHEN** an invocation supplies a workflow stage outside the consolidated workflow stage set
- **THEN** resolution fails visibly instead of publishing the unknown value as ordinary context
