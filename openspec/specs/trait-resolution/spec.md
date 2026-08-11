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
An evidence-selected flavor SHALL contribute each declared facet missing from the resolution context to the result. Equal contributions SHALL be deduplicated. Distinct string contributions to the same previously missing categorical facet SHALL become an ordered list following retained flavor order. Evidence SHALL NOT overwrite or expand a known conflicting facet or cause ZPP to restart trait selection recursively during the same resolution.

#### Scenario: Backfill detected language
- **WHEN** workspace evidence selects a flavor declaring the Python language facet and no language is known
- **THEN** the resolution result contains the Python facet together with the selected body

#### Scenario: Preserve known context
- **WHEN** a candidate flavor's facet conflicts with an explicitly known context value
- **THEN** ZPP excludes that candidate and does not replace the known value

#### Scenario: Backfill several detected languages
- **WHEN** selected evidence-backed flavors contribute Python and Flutter to a previously missing language facet
- **THEN** the result contains `language = ["python", "flutter"]` in retained flavor order

### Requirement: Repository and environment context inputs
Resolution SHALL accept repository-known scalar or multi-value string facets from the `[facet]` table in `.zpp/zpp.toml`, an explicitly supplied workflow stage, and compatible stored context from a ZPP-owned session environment value. Explicit invocation context SHALL take precedence over repository context, and both SHALL take precedence over evidence-backfilled context.

#### Scenario: Resolve with repository-known facets
- **WHEN** `.zpp/zpp.toml` declares Python and Click facets and the workflow explicitly requests the shape stage
- **THEN** resolution uses those exact values during the direct facet pass

#### Scenario: Preserve explicit stage authority
- **WHEN** stored environment context contains a different stage from the explicitly requested workflow action
- **THEN** the explicit action supplies the stage used for resolution

### Requirement: Stored backfilled session context
ZPP SHALL serialize updated stored context as one compact JSON `ZPP_CONTEXT` value that its supported session integration can publish for later invocations. The complete value SHALL include facet values, value provenance, selected target identity, and relevant evidence fingerprints. Publication SHALL replace the prior complete value. A target mismatch SHALL invalidate the stored context, and changed evidence SHALL invalidate affected evidence-derived values. Stored values SHALL NOT grant mutation, stage-transition, or completion authority.

#### Scenario: Carry detected language into a later invocation
- **WHEN** evidence selection backfills the Python facet and the session integration publishes the returned context
- **THEN** a later compatible invocation can receive Python as stored context without treating it as workflow authority

#### Scenario: Ignore context from another target
- **WHEN** `ZPP_CONTEXT` identifies a repository target different from the current selected target
- **THEN** resolution ignores that stored context instead of applying its facets

#### Scenario: Invalidate changed evidence
- **WHEN** stored context derives a facet from fingerprinted workspace evidence that has changed
- **THEN** resolution invalidates that derived value before matching trait flavors

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

### Requirement: Explain deterministic selection
ZPP SHALL provide an explanation of the known context, effective flavor order, facet decisions, selection policy decisions, dominance decisions, evidence decisions, retained flavors, backfilled facets, and source provenance without changing the resolution result.

#### Scenario: Explain an evidence-selected flavor
- **WHEN** a user requests an explanation for a trait selected through workspace evidence
- **THEN** ZPP identifies the rejected earlier flavors, successful evidence branch, selected source and position, selection-policy result, and every backfilled facet
