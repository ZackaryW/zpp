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

### Requirement: Resolution reports the effective governance context
For a directory associated with a valid single-store workset, zpp SHALL report both the stable registered store identity/base root and the session-effective governance branch/root. The effective context SHALL also name the logical project member and project branch used for derivation. Config and trait consumers SHALL use the effective root while store-id validation continues to use the global registry.

#### Scenario: Isolated feature context resolves
- **WHEN** resolution runs in an aliased `project-a` checkout on `feature-x` whose governance worktree is provisioned
- **THEN** the result retains the registered store id and base root and reports `project-a/feature-x` plus its worktree as the effective governance context

### Requirement: Invalid or unprovisioned isolation fails closed
Resolution SHALL NOT silently fall back to the globally registered base store when a recognized project context requires isolation. A multi-store workset SHALL return an invalid-workset failure, and a missing derived governance checkout SHALL return a provisioning-required failure. Both failures SHALL carry machine-readable evidence and human remediation.

#### Scenario: Missing worktree cannot bleed into base
- **WHEN** a feature checkout uniquely matches a store-backed workset but its derived governance worktree is absent
- **THEN** resolution does not return the registered base root as effective and instead requires provisioning

#### Scenario: Invalid multi-store workset cannot choose
- **WHEN** the containing workset has more than one dedicated store
- **THEN** resolution fails without selecting a store by path order, member order, or profile

### Requirement: Store references validate against the openspec registry
Any store id used in resolution SHALL be validated against openspec's store registry, read-only. zpp SHALL distinguish a local root (an `openspec/` directory) from a registered store (`.openspec-store/store.yaml` plus a registry entry) and SHALL never write to the registry.

#### Scenario: Binding to a vanished store
- **WHEN** a binding references a store id no longer present in the registry
- **THEN** resolution reports the mode with a dangling-store warning naming the missing id

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

### Requirement: Resolution reports assigned reference stores
Resolution SHALL report the containing workset's assigned reference stores by
id and root, distinctly from the governing store, so that a listed reference
store can never be read as the governing authority. Reference store
assignments SHALL NOT affect mode, rule selection, store binding, effective
root, governance branch, isolation state, or lease keying. When a workset has
no assignments, or the path belongs to no workset, resolution SHALL report an
empty set rather than omitting the distinction.

#### Scenario: Reference stores reported beside the governing store
- **WHEN** resolution runs for a member of a workset with one assigned
  reference store
- **THEN** the result names the governing store as it always did and reports
  the assigned reference store separately with its id and root

#### Scenario: Assignment does not alter resolution
- **WHEN** the same directory is resolved before and after a reference store
  is assigned
- **THEN** mode, rule, store binding, effective root, and isolation state are
  identical in both results

#### Scenario: No assignments
- **WHEN** resolution runs for a workset with no assigned reference stores
- **THEN** the reported reference-store set is empty rather than absent

