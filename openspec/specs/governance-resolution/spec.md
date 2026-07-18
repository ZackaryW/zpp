# governance-resolution

## Purpose

Give every directory exactly one governance answer: which of the four modes it is in, which store governs it, and what its effective layered configuration is. This fills the binding gap openspec deliberately leaves open (openspec models stores and local roots, never project→store bindings).

## Requirements

### Requirement: Four-mode governance resolution
Given a directory, zpp SHALL resolve its governance mode by the first matching rule: (1) an `openspec/` root in the directory's ancestry → self-governed; (2) an in-repo `zpp.toml` binding to a store → externally governed by committed fact; (3) the directory is a workset member whose resolved profile declares `[governance] store` → externally governed by workset profile; (4) otherwise → ungoverned. The resolution result SHALL name the mode, the governing store id (when applicable), and which rule matched.

#### Scenario: Self-governed repo
- **WHEN** resolution runs inside a repo containing a local `openspec/` root
- **THEN** the mode is self-governed and no store binding is consulted

#### Scenario: Committed binding wins over profile
- **WHEN** a repo's `zpp.toml` binds it to store A and its workset profile declares store B
- **THEN** resolution reports store A by rule 2, and the disagreement is reported by doctor rather than silently merged

#### Scenario: Profile supplies the binding
- **WHEN** a repo with no committed binding is a workset member whose resolved profile declares `[governance] store = "gov"`
- **THEN** resolution reports externally-governed by rule 3 with store `gov` and names the workset and profile

#### Scenario: Ungoverned is explicit
- **WHEN** no rule matches
- **THEN** zpp reports the directory as ungoverned, not an error

### Requirement: Store references validate against the openspec registry
Any store id used in resolution SHALL be validated against openspec's store registry, read-only. zpp SHALL distinguish a local root (an `openspec/` directory) from a registered store (`.openspec-store/store.yaml` plus a registry entry) and SHALL never write to the registry.

#### Scenario: Binding to a vanished store
- **WHEN** a binding references a store id no longer present in the registry
- **THEN** resolution reports the mode with a dangling-store warning naming the missing id

### Requirement: Layered config resolution
`zpp config resolve` SHALL compute the effective configuration by layering, in order of decreasing precedence: the governed repo's `zpp.toml` (top level, excluding `[profiles.*]`), the member's resolved workset profile, and the governing store's published `default` profile — declared as `[profiles.default]` (with one-level `extends` resolved) inside the store's own `zpp.toml`. There is no separate store defaults file. Scalar values SHALL override lower layers; list values SHALL union with lower layers. The output SHALL be available as JSON and SHALL identify, on request, which layer supplied each value.

#### Scenario: Scalar override
- **WHEN** the store default sets `zmem.mode = "present"` and the repo `zpp.toml` sets `zmem.mode = "apply"`
- **THEN** the effective value is `"apply"` sourced from the repo layer

#### Scenario: Profile is the middle tier
- **WHEN** the member's resolved profile sets a value the store default also sets
- **THEN** the profile value wins over the store default and loses to the repo `zpp.toml`

#### Scenario: List union
- **WHEN** the store default declares list entries and the repo adds further entries
- **THEN** the effective list is the union of both layers

#### Scenario: Self-governed repo config
- **WHEN** the repo is self-governed (rule 1)
- **THEN** its own `zpp.toml` serves both layers - `[profiles.default]` as the store tier, the top level as the repo tier - without requiring an external store
