# TOML Trait Catalog Specification

## Purpose

Define readable one-family TOML traits, strict validation, and deterministic source composition.

## Requirements

### Requirement: One trait family per TOML document
ZPP SHALL derive one trait-family name from each `{name}.toml` document basename. The document SHALL contain a `[meta]` table with a supported `selection` policy, MAY contain a supported family-level `activation` mode, and SHALL contain an ordered array of flavors beneath `[[trait]]`. Omitted activation SHALL mean `automatic`. Each flavor SHALL retain its authored position within its effective source and MAY declare a facet table and one or more workspace-evidence branches.

#### Scenario: Decode several flavors for one trait
- **WHEN** `bdd.toml` declares `[meta] selection = "extend"` and several `[[trait]]` entries
- **THEN** ZPP exposes them as ordered flavors of the `bdd` family using the declared `extend` policy and automatic activation

#### Scenario: Decode explicit activation
- **WHEN** one family declares `[meta] activation = "manual"`
- **THEN** ZPP exposes manual as that document's family activation mode

#### Scenario: Reject several families in one file
- **WHEN** one trait document attempts to declare independently named trait families
- **THEN** ZPP rejects it because the document basename supplies its one family identity

#### Scenario: Reject unsupported activation
- **WHEN** a trait document declares an activation value other than automatic, manual, or always-run
- **THEN** the complete document fails validation and identifies `[meta].activation`

### Requirement: Complete retained content body
Every trait flavor SHALL contain a `content` table with a textual `body`. ZPP SHALL preserve that complete body as the flavor's human-readable instruction and SHALL NOT require inheritance, fragment inclusion, or body generation from another flavor.

#### Scenario: Preserve repeated ecosystem guidance
- **WHEN** Python and Flutter flavors repeat shared paragraphs with ecosystem-specific wording
- **THEN** each flavor retains and returns its own complete authored body without cross-flavor composition

### Requirement: Document-oriented validation
ZPP SHALL reject a trait document containing invalid metadata or an invalid flavor without accepting a partial subset from that document. A validation failure SHALL identify the source, trait family, flavor position when applicable, and invalid field without emitting a stack trace.

#### Scenario: Reject one invalid flavor atomically
- **WHEN** one flavor in a trait document lacks its required content body or contains an invalid declared structure
- **THEN** the complete document fails validation and the diagnostic identifies that flavor

#### Scenario: Reject missing selection metadata
- **WHEN** a trait document omits `[meta].selection` or names an unsupported policy
- **THEN** the complete document fails validation and the diagnostic identifies the metadata field

### Requirement: No implicit flavor inheritance
Trait flavors SHALL remain independent. ZPP SHALL NOT infer inheritance, template expansion, provider dependencies, or a capability graph from shared facet values, neighboring flavors, or repeated content.

#### Scenario: Keep similar flavors independent
- **WHEN** two flavors declare related facets and similar bodies
- **THEN** changing one flavor does not alter the decoded content or metadata of the other

### Requirement: Repository-space-global composition
When OpenLease sources contribute same-basename trait documents to the same trait family, ZPP SHALL compose the effective family in repository → space → global order. ZPP SHALL preserve the established order within each source category and authored flavor order within each document. The highest-precedence contributing document's `selection` and `activation` SHALL be the effective family policies, with omitted activation interpreted as `automatic`.

#### Scenario: Override one repository specialization and retain defaults
- **WHEN** repository `bdd.toml` contributes Python-and-Click, space `bdd.toml` contributes Python, and global `bdd.toml` contributes Flutter
- **THEN** the effective flavor order is repository Python-and-Click, space Python, then global Flutter

#### Scenario: Use the highest-precedence family policies
- **WHEN** repository and global documents contribute to one family with different `selection` and `activation` values
- **THEN** the repository document's selection and activation govern the complete layered family

#### Scenario: Preserve source-local order
- **WHEN** one source contributes several ordered flavors to a trait family
- **THEN** those flavors remain in their authored order relative to one another after layered composition

### Requirement: Explicit repository overwrite mode
A repository trait document MAY declare `[meta] mode = "repository-overwrite"`. When declared, ZPP SHALL exclude every space and global contribution to that family before selection. When `mode` is omitted, ZPP SHALL use repository-space-global layered composition. ZPP SHALL reject `repository-overwrite` on a non-repository contribution.

#### Scenario: Replace inherited family contributions
- **WHEN** repository `bdd.toml` declares `mode = "repository-overwrite"` while space and global `bdd.toml` documents also exist
- **THEN** the effective `bdd` family contains only repository flavors and uses the repository selection policy

#### Scenario: Layer by default
- **WHEN** repository `bdd.toml` omits `mode` while space and global `bdd.toml` documents exist
- **THEN** all three documents contribute in repository-space-global order

#### Scenario: Reject overwrite outside repository scope
- **WHEN** a space or global trait document declares `mode = "repository-overwrite"`
- **THEN** ZPP rejects that source declaration as invalid

### Requirement: Scalar flavor constraints and scalar-or-list context
Trait flavor facet constraints SHALL be strings. Repository-known and explicitly supplied categorical context facets SHALL be either strings or non-empty lists of distinct strings. A scalar flavor constraint SHALL match an equal scalar context value or a member of the corresponding context list. ZPP SHALL reject tables, non-string categorical values, empty lists, and lists containing duplicates or non-strings. Runtime boolean facets produced by registered evidence predicates SHALL remain separately typed derived context rather than authored categorical facets.

#### Scenario: Accept an authored language facet
- **WHEN** a trait flavor declares `language = "python"`
- **THEN** ZPP accepts the facet as the exact string value `python`

#### Scenario: Accept a multi-language repository context
- **WHEN** repository context declares `language = ["python", "flutter"]`
- **THEN** both scalar flavor constraints can independently match that context value

#### Scenario: Reject an authored boolean facet
- **WHEN** a trait flavor authors `has_uv = true` directly in its facet table
- **THEN** document validation rejects that non-string constraint rather than confusing it with predicate-derived runtime evidence
