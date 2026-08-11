# Trait Resolution Specification

## Purpose

Define deterministic facet and evidence matching, selection, backfill, context persistence, and explanations.

## Requirements

### Requirement: Complete facet matching
For each effective trait family, ZPP SHALL identify every flavor for which each declared scalar facet constraint is satisfied by the corresponding scalar or multi-value known context facet. A missing or conflicting facet SHALL NOT match that flavor.

#### Scenario: Match flavors against a multi-value context
- **WHEN** the known context declares Python and Flutter and the family contains one flavor constrained to each language
- **THEN** both flavors enter the matching set before the selection policy is applied

#### Scenario: Reject a partial facet match
- **WHEN** a flavor requires both Python and Click facets but the context contains only Python
- **THEN** that flavor does not enter the matching set

### Requirement: Explicit selection policy
ZPP SHALL apply the selection policy from the highest-precedence contributing document to the effective family's matching flavors. `first-win` SHALL retain only the first matching flavor in repository → space → global effective order. `all` SHALL retain every matching flavor in effective order. `extend` SHALL remove a matching flavor when another matching flavor's facet constraint map is a strict superset of it and SHALL retain incomparable matches in effective order. Equal facet maps SHALL retain only their first matching flavor under `extend`.

#### Scenario: Retain the first match
- **WHEN** a `first-win` family has matching repository, space, and global flavors
- **THEN** ZPP returns only the first repository match

#### Scenario: Retain all matches
- **WHEN** an `all` family has several matching flavors
- **THEN** ZPP returns every matching flavor in effective order

#### Scenario: Strip a generic match under extend
- **WHEN** an `extend` family matches generic Python, Python-and-uv, and Flutter flavors for context containing Python, Flutter, and uv
- **THEN** ZPP returns Python-and-uv and Flutter while removing generic Python as dominated

#### Scenario: Retain incomparable specializations
- **WHEN** an `extend` family matches Python-and-uv and Python-and-Click flavors
- **THEN** ZPP returns both because neither flavor's facet constraint map contains the other

### Requirement: First-win compatible evidence fallback
When no flavor directly matches in a `first-win` family, ZPP SHALL scan the same flavors in effective authored order, exclude flavors whose declared facets conflict with known context, and select the first remaining flavor with a successful declared `when` branch. A flavor without a `when` branch SHALL NOT act as an implicit unconditional fallback.

#### Scenario: Detect a Flutter flavor from workspace evidence
- **WHEN** no language facet is known and the first compatible evidence-backed flavor detects the accepted Flutter workspace evidence
- **THEN** ZPP selects that flavor and does not evaluate later flavors as potential winners

#### Scenario: Ignore a facet-only flavor during fallback
- **WHEN** no known facets select a flavor and an ordered flavor declares no `when` branch
- **THEN** ZPP skips that flavor during evidence fallback

### Requirement: Multi-winner evidence candidates
For an `all` or `extend` family, ZPP SHALL form the policy candidate set from every directly matching flavor plus every compatible flavor with a successful declared `when` branch. A flavor SHALL be compatible only when none of its declared facets conflicts with known context. ZPP SHALL apply the family selection policy after forming this combined candidate set.

#### Scenario: Add an evidence-backed specialization under extend
- **WHEN** generic Python matches directly and compatible Python-and-uv evidence succeeds in an `extend` family
- **THEN** both enter the candidate set and Python-and-uv removes generic Python through facet dominance

#### Scenario: Retain direct and evidence matches under all
- **WHEN** one flavor matches directly and two other compatible flavors have successful evidence in an `all` family
- **THEN** all three flavors are returned in effective order

#### Scenario: Exclude conflicting evidence candidate
- **WHEN** explicit context identifies uv and a Poetry flavor's evidence succeeds
- **THEN** the Poetry flavor remains excluded because its declared build-tool facet conflicts with explicit context

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

### Requirement: Initial evidence predicate set
The initial trait evidence schema SHALL support `workspace_contains`, literal `file_contains`, and `which`. A leading `/` SHALL anchor a workspace pattern to the selected target root. `file_contains` SHALL explicitly name its target file and literal text. A `which` check SHALL test executable availability and record its result as a boolean runtime facet named `has_<tool>`.

#### Scenario: Match a root project file
- **WHEN** `workspace_contains` names `/pyproject.toml` and that file exists at the selected target root
- **THEN** the predicate succeeds without matching a nested `pyproject.toml` instead

#### Scenario: Match literal project content
- **WHEN** `file_contains` names `/pyproject.toml` and the literal text `click`
- **THEN** it succeeds only when that exact file contains the requested literal text

#### Scenario: Record an available tool
- **WHEN** resolution evaluates `which = "uv"` and `uv` is available to the current process
- **THEN** the predicate succeeds and the result contains boolean facet `has_uv = true`

#### Scenario: Record an unavailable tool
- **WHEN** resolution evaluates `which = "uv"` and `uv` is unavailable to the current process
- **THEN** the predicate fails and the result contains boolean facet `has_uv = false`

### Requirement: Complete selected bodies per trait family
One resolution SHALL return the complete `content.body` of every flavor retained by the family's selection policy in deterministic effective order. No retained flavor SHALL produce partial body output.

#### Scenario: Resolve one first-win BDD body
- **WHEN** one `bdd` flavor wins `first-win` facet or evidence selection
- **THEN** exactly that flavor's complete body is returned for `bdd`

#### Scenario: Resolve several extend bodies
- **WHEN** two incomparable `bdd` flavors remain after `extend` dominance filtering
- **THEN** both complete bodies are returned for `bdd` in effective order

#### Scenario: Resolve no BDD body
- **WHEN** no `bdd` flavor is retained
- **THEN** `bdd` remains inactive and contributes no partial or fallback content

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

### Requirement: Explain deterministic selection
ZPP SHALL provide an explanation of the known context, effective flavor order, facet decisions, selection policy decisions, dominance decisions, evidence decisions, retained flavors, backfilled facets, and source provenance without changing the resolution result.

#### Scenario: Explain an evidence-selected flavor
- **WHEN** a user requests an explanation for a trait selected through workspace evidence
- **THEN** ZPP identifies the rejected earlier flavors, successful evidence branch, selected source and position, selection-policy result, and every backfilled facet
