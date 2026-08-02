## Purpose

Defines the authored trait document contract and source-authoritative cache behavior used by every participating resolution layer.

## ADDED Requirements

### Requirement: Authored trait document
Each authored trait SHALL be one UTF-8 Markdown file with YAML frontmatter followed by an advisory body. Frontmatter MUST contain `name` and `description`, MAY contain a non-negative integer `order`, a JSON-compatible mapping `config`, and an ordered string list `skill_lookup`, and MUST reject unknown fields. The filename stem MUST equal `name`.

Existing authored source, including advisory-body whitespace and Unicode text, SHALL remain byte-unchanged during validation, compilation, caching, and resolution. `skill_lookup` SHALL remain passive advisory metadata.

#### Scenario: Accept a complete trait document
- **WHEN** a participating layer contains a valid trait with any accepted optional frontmatter and UTF-8 advisory content
- **THEN** its normalized effective record retains the accepted metadata and exact advisory body without rewriting the authored file

#### Scenario: Reject invalid authored traits
- **WHEN** a participating collection contains documents with invalid envelopes, metadata, identities, or encoding
- **THEN** the complete collection is rejected with every invalid authored source identified

### Requirement: Participating-layer compilation
ZPP SHALL compile the complete authored Markdown collection of each participating layer lazily. It SHALL NOT compile or create caches for inactive user layers.

Compilation SHALL produce one deterministic, normalized trait index for the complete layer or no usable result. Duplicate trait identities or any source validation failure SHALL reject the complete compilation rather than expose a valid subset.

#### Scenario: Compile participating layers only
- **WHEN** resolution includes valid participating layers while other user layers remain inactive
- **THEN** only participating collections receive normalized derived indexes and every authored source remains unchanged

### Requirement: Independent derived cache
Each trait index and its freshness certification SHALL live in derived state independent from authored layer sources. Repository-local derived state SHALL remain structurally separate from authored traits, and user-level global, profile, and saved caches SHALL remain independently namespaced.

Cache representation and freshness metadata SHALL NOT alter the meaning or public representation of an effective trait.

#### Scenario: Reuse a current derived index
- **WHEN** a participating authored collection is unchanged since a complete cache generation
- **THEN** ZPP may reuse that certified index without rewriting source or exposing cache metadata

### Requirement: Source-authoritative rebuild
Authored Markdown SHALL supersede derived data whenever freshness certification is absent, invalid, or older than participating source state. ZPP SHALL complete validation and compilation before certifying a replacement cache.

A rebuild failure SHALL fail the complete resolution and SHALL NOT return an older index, a partial index, or a valid subset, even if old derived files remain physically present.

#### Scenario: Rebuild after an authored change
- **WHEN** a participating authored trait changes after its current cache was certified
- **THEN** resolution uses the changed source and never returns the preceding advisory content

#### Scenario: Reject a failed rebuild without fallback
- **WHEN** stale derived data exists and one or more participating authored traits are invalid
- **THEN** resolution fails with all invalid sources identified and emits no stale or partial trait output
