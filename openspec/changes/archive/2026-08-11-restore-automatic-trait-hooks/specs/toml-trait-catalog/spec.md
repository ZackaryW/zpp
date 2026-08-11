## MODIFIED Requirements

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
