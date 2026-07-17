# governance-resolution

## Purpose

Give every directory exactly one governance answer: which of the four modes it is in, which store governs it, and what its effective layered configuration is. This fills the binding gap openspec deliberately leaves open (openspec models stores and local roots, never project→store bindings).

## Requirements

### Requirement: Four-mode governance resolution
Given a directory, zpp SHALL resolve its governance mode by the first matching rule: (1) an `openspec/` root in the directory's ancestry → self-governed; (2) an in-repo `zpp.toml` binding to a store → externally governed by committed fact; (3) a workset sidecar binding covering the directory → externally governed by personal view; (4) otherwise → ungoverned. The resolution result SHALL name the mode, the governing store id (when applicable), and which rule matched.

#### Scenario: Self-governed repo
- **WHEN** resolution runs inside a repo containing a local `openspec/` root
- **THEN** the mode is self-governed and no store binding is consulted

#### Scenario: Committed binding wins over personal view
- **WHEN** a repo's `zpp.toml` binds it to store A and a workset sidecar binds the same repo to store B
- **THEN** resolution reports store A by rule 2, and the disagreement is reported by doctor rather than silently merged

#### Scenario: Ungoverned is explicit
- **WHEN** no rule matches
- **THEN** zpp reports the directory as ungoverned, not an error

### Requirement: Store references validate against the openspec registry
Any store id used in resolution SHALL be validated against openspec's store registry, read-only. zpp SHALL distinguish a local root (an `openspec/` directory) from a registered store (`.openspec-store/store.yaml` plus a registry entry) and SHALL never write to the registry.

#### Scenario: Binding to a vanished store
- **WHEN** a binding references a store id no longer present in the registry
- **THEN** resolution reports the mode with a dangling-store warning naming the missing id

### Requirement: Layered config resolution
`zpp config resolve` SHALL compute the effective configuration by layering, in order of decreasing precedence: the governed repo's `zpp.toml`, the workset sidecar's project-scoped overlay, and the governing store's `zpp.default.toml`. Scalar values SHALL override lower layers; list values SHALL union with lower layers. The output SHALL be available as JSON and SHALL identify, on request, which layer supplied each value.

#### Scenario: Scalar override
- **WHEN** the store default sets `zmem.mode = "present"` and the repo `zpp.toml` sets `zmem.mode = "apply"`
- **THEN** the effective value is `"apply"` sourced from the repo layer

#### Scenario: List union
- **WHEN** the store default declares `[agent]` shards and the repo adds further shards
- **THEN** the effective list is the union of both layers

#### Scenario: Self-governed repo config
- **WHEN** the repo is self-governed (rule 1)
- **THEN** its own root's config files serve as both the repo and store layers without requiring an external store
