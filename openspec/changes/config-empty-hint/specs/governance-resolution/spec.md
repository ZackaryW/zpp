# Delta: governance-resolution

## MODIFIED Requirements

### Requirement: Layered config resolution
`zpp config resolve` SHALL compute the effective configuration by layering, in order of decreasing precedence: the governed repo's `zpp.toml` (top level, excluding `[profiles.*]`), the member's resolved workset profile, and the governing store's published `default` profile — declared as `[profiles.default]` (with one-level `extends` resolved) inside the store's own `zpp.toml`. There is no separate store defaults file. Scalar values SHALL override lower layers; list values SHALL union with lower layers. The output SHALL be available as JSON and SHALL identify, on request, which layer supplied each value.

When the effective configuration is empty, the human-readable output SHALL
append a one-line authoring hint — no `zpp.toml` was found; author one, see
the documented template. The hint SHALL appear only on the human surface:
JSON output SHALL remain the bare empty result, and zpp SHALL NOT create the
file itself (owner-authored by doctrine).

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

#### Scenario: Empty config carries the authoring hint
- **WHEN** `zpp config resolve` runs in a context with no `zpp.toml`, no
  applicable profile, and no store default
- **THEN** the human output states the configuration is empty and hints at
  authoring a `zpp.toml` from the documented template, while `--json` returns
  the empty result unchanged and no file is created
