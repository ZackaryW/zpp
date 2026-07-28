## MODIFIED Requirements

### Requirement: Layered config resolution
`zpp config resolve <PATH>` SHALL compute effective configuration for the concrete target by layering, in order of increasing precedence: the governing store's published `default` profile — declared as `[profiles.default]` (with one-level `extends` resolved) inside the store's own `zpp.toml` — the member's resolved workset profile, the governed repository root's `zpp.toml` top level excluding `[profiles.*]`, and every descendant `zpp.toml` from the repository root toward the target. A file target SHALL resolve scopes from its parent directory. There is no separate store defaults file. Scalar values SHALL override lower layers; list values SHALL union with lower layers without duplicates; table values SHALL merge recursively. The output SHALL be available as JSON and `--sources --json` SHALL identify the ordered scoped files and the exact layer supplying each value.

When the effective configuration is empty, the human-readable output SHALL append a one-line authoring hint — no `zpp.toml` was found; author one, see the documented template. The hint SHALL appear only on the human surface: JSON output SHALL remain the bare empty result, and zpp SHALL NOT create the file itself (owner-authored by doctrine).

#### Scenario: Scalar override
- **WHEN** the store default sets `zmem.mode = "present"` and the repository root `zpp.toml` sets `zmem.mode = "apply"`
- **THEN** the effective value is `"apply"` sourced from the repository layer

#### Scenario: Profile is the middle tier
- **WHEN** the member's resolved profile sets a value the store default also sets
- **THEN** the profile value wins over the store default and loses to the repository and any applicable scoped overlay

#### Scenario: List union
- **WHEN** the store default declares list entries and the repository or a nested scope adds further entries
- **THEN** the effective list is their duplicate-free union in layer order

#### Scenario: Self-governed repo config
- **WHEN** the repository is self-governed (rule 1)
- **THEN** its root `zpp.toml` serves both root layers — `[profiles.default]` as the store tier and the top level as the repository tier — without requiring an external store

#### Scenario: Nested scalar selects a subtree stack
- **WHEN** the repository root sets `tdd.stack = "rust"`, `sdk/python/zpp.toml` sets `tdd.stack = "python"`, and resolution targets `sdk/python/src`
- **THEN** the effective TDD stack is `"python"`, sourced from `sdk/python/zpp.toml`

#### Scenario: Root does not inherit child config
- **WHEN** only `sdk/python/zpp.toml` declares Python BDD and TDD stacks
- **THEN** resolution for the repository root excludes those stacks while resolution for `sdk/python` and its descendants includes them

#### Scenario: Multiple nested scopes merge in ancestry order
- **WHEN** both `sdk/zpp.toml` and `sdk/python/zpp.toml` declare ordinary configuration and resolution targets `sdk/python/src`
- **THEN** zpp merges `sdk` before `sdk/python`, and source reporting lists both canonical files in that order

#### Scenario: Empty config carries the authoring hint
- **WHEN** `zpp config resolve` runs in a context with no root config, no applicable nested config, no applicable profile, and no store default
- **THEN** the human output states the configuration is empty and hints at authoring a `zpp.toml` from the documented template, while `--json` returns the empty result unchanged and no file is created

## ADDED Requirements

### Requirement: Scoped config remains inside one governance root
Nested ordinary configuration SHALL NOT alter governance mode, store identity, effective governance root, isolation state, governance branch, workset membership, or lease identity. zpp SHALL canonicalize the target and gather scoped files only between the already-resolved governance root and that target. It SHALL NOT consume a scoped file outside that root or from a sibling subtree.

#### Scenario: Sibling scope does not leak
- **WHEN** `sdk/python/zpp.toml` declares a Python stack and resolution targets `crates/core`
- **THEN** the Python scope is absent from the effective configuration

#### Scenario: Governance answer is stable across scopes
- **WHEN** configuration is resolved at both the repository root and a nested configured subtree
- **THEN** both results carry the same governance mode, store, effective root, isolation state, and lease context

#### Scenario: Canonical target cannot escape the root
- **WHEN** a target path resolves outside the governance root through parent traversal or a filesystem indirection
- **THEN** zpp does not read scoped configuration across the root boundary

### Requirement: Authority sections are root-only
A descendant `zpp.toml` used as a scoped overlay SHALL NOT declare `[governance]` or `[profiles]` content. If either section is present, config resolution SHALL fail before merging any part of that file and SHALL name the canonical file and every prohibited section. The governance root's own file retains its existing authority and publication semantics.

#### Scenario: Nested governance binding fails clearly
- **WHEN** `sdk/python/zpp.toml` declares `[governance] store = "other"`
- **THEN** config resolution fails naming `sdk/python/zpp.toml` and `[governance]`, while `zpp resolve` continues to report the repository's established governance root

#### Scenario: Nested profiles fail clearly
- **WHEN** a descendant file declares `[profiles.default]`
- **THEN** config resolution fails naming that file and `[profiles]` rather than publishing or silently ignoring the profile

#### Scenario: Ordinary nested sections remain valid
- **WHEN** a descendant file declares only ordinary sections such as `[tdd]`, `[bdd]`, `[doctor]`, `[traits]`, or `[test-economy]`
- **THEN** those sections participate in scoped resolution normally
