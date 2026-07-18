# workset-management

## Purpose

Adopt user-owned `.code-workspace` files as openspec worksets and carry the governance semantics openspec refuses to hold: config profiles, member roles, and drift detection. Layout truth stays in the workspace file; profiles live in the machine-local sidecar or a committed `.zpp-workset` file beside the workspace.

## Requirements

### Requirement: Import a .code-workspace as a workset
`zpp workset import <file.code-workspace>` SHALL parse the workspace file (tolerating JSONC), resolve each folder's relative path to an absolute path against the workspace file's own directory, create the corresponding openspec workset via the `openspec workset` CLI, and write a sidecar under `~/.zpp/worksets/<name>.toml` recording the source workspace file path and member metadata keyed by member name. The workset name SHALL satisfy openspec's kebab-case naming rules.

#### Scenario: Successful import
- **WHEN** the user runs `zpp workset import ./pathverse.code-workspace` and no workset of that name exists
- **THEN** an openspec workset is created whose members match the workspace file's folders with absolute paths, and a sidecar exists recording the workspace file's absolute path

#### Scenario: Member folder missing on this machine
- **WHEN** a folder listed in the workspace file does not exist on disk
- **THEN** the import reports the missing member and fails without creating a partial workset, unless the user passes an explicit flag to import the surviving members

#### Scenario: Name collision
- **WHEN** an openspec workset with the derived name already exists
- **THEN** zpp refuses and instructs the user to choose another name or remove the existing workset; it SHALL NOT overwrite openspec-owned state

### Requirement: One-way sync from the workspace file
`zpp workset sync [name]` SHALL re-read the sidecar-recorded `.code-workspace` file and reconcile the openspec workset and sidecar to match its folders. zpp SHALL NOT write to the `.code-workspace` file under any command. Member metadata SHALL follow members across renames when folder `name` labels are present; when a change is indistinguishable from remove+add, sync SHALL present its reconciliation plan before applying metadata-destructive changes.

#### Scenario: Folder added in VSCode
- **WHEN** the user adds a folder to the workspace file and runs `zpp workset sync`
- **THEN** the openspec workset gains the member and the sidecar gains an entry with no bindings

#### Scenario: Labeled folder renamed
- **WHEN** a folder entry with a stable `name` label changes its `path` and the user syncs
- **THEN** the member's sidecar metadata (bindings, role) is preserved under the same name with the updated path

#### Scenario: Unlabeled folder replaced
- **WHEN** an unlabeled folder disappears and a new one appears in the workspace file
- **THEN** sync shows a plan identifying the metadata that would be dropped and requires confirmation before applying

### Requirement: Delegation to openspec workset
Workset composition, opening, listing, and removal SHALL be delegated to the `openspec workset` CLI (using `--json` output where available). zpp SHALL NOT write to any file under openspec's data directory.

#### Scenario: Opening a workset
- **WHEN** the user runs `zpp workset open <name>`
- **THEN** zpp invokes `openspec workset open <name>` and surfaces its outcome unchanged

#### Scenario: Removing a workset through zpp
- **WHEN** the user runs `zpp workset remove <name>`
- **THEN** zpp delegates removal to openspec and deletes the sidecar and its snapshots

### Requirement: Workset config profiles
A workset's config SHALL be organized as named profiles — `[profiles.<name>]` blocks in zpp.toml shape. Every member SHALL resolve to the profile named `default`; a member entry MAY point at another profile with `profile = "<name>"`. The resolved profile is the member's workset config tier (below the repo's own `zpp.toml`, above store defaults). A profile MAY declare `extends = "<name>"`: the parent's config is merged under the child's (child wins; one level only, no chains). A member pointing at a profile that does not exist SHALL be reported by doctor; absence of a `default` profile means unpointed members have an empty workset tier.

#### Scenario: Members resolve to the default profile
- **WHEN** a workset defines `[profiles.default]` with `[traits] apply = ["ponytail"]` and member `api` has no profile pointer
- **THEN** `api`'s effective config includes ponytail from the workset tier

#### Scenario: Explicit pointer selects another profile
- **WHEN** member `web` declares `profile = "webapp"` and `[profiles.webapp]` sets `[governance] store = "governance-of-appbuilder"`
- **THEN** `web` resolves that store binding from its profile while `api` keeps the default profile

#### Scenario: Repo config overrides the profile
- **WHEN** a member's profile sets a scalar and the member repo's `zpp.toml` sets the same key differently
- **THEN** the repo value wins, per the standard tier order

#### Scenario: A profile extends another
- **WHEN** `[profiles.store-dev]` declares `extends = "default"` plus a store binding, and `default` applies traits
- **THEN** a member pointing at `store-dev` gets the inherited traits and the binding

#### Scenario: Dangling profile pointer
- **WHEN** a member points at a profile name that is not defined
- **THEN** the member gets an empty workset tier and `zpp workset doctor` reports the dangling pointer

### Requirement: Shared workset config file
When a file named `<stem>.zpp-workset` exists beside `<stem>.code-workspace`, it SHALL be the source of truth for the workset's profiles and member profile pointers. The file SHALL reference members by name only — never by path; member paths always derive from the `.code-workspace` on each machine. When the file is absent, profiles live in the machine-local sidecar under `~/.zpp`. The two homes SHALL never merge: the shared file, when present, wins entirely. `zpp workset sync` SHALL never create or delete the shared file.

#### Scenario: Shared file wins over the sidecar
- **WHEN** both a `.zpp-workset` file and sidecar profiles exist for a workset
- **THEN** profiles and pointers come from the shared file and the sidecar's profile content is ignored

#### Scenario: Portable across machines
- **WHEN** a teammate clones a folder containing the `.code-workspace` and `.zpp-workset` pair and runs `zpp workset import`
- **THEN** the workset resolves the same profiles and pointers with paths derived from the workspace file on that machine

#### Scenario: Personal fallback
- **WHEN** no `.zpp-workset` file exists
- **THEN** profiles are read from the `~/.zpp` sidecar as machine-local personal config

### Requirement: Workset status and doctor
`zpp workset status` SHALL report, for the current workset context: members, each member's **live** governance resolution (mode and store as `zpp resolve` would report them), the profile each member resolves to, which config home is active (shared `.zpp-workset` file or personal sidecar), and the source workspace file. `zpp workset doctor` SHALL detect and report: sidecars whose openspec workset no longer exists, openspec worksets lacking sidecars, member paths that do not exist, source workspace files that have moved or disappeared, profile pointers naming undefined profiles, shared-file member entries naming members the workspace lacks, profiles binding unregistered stores, and repos that are members of multiple worksets (warning that names the alphabetically-first winner and the shadowed worksets).

#### Scenario: Status reflects live resolution and profile
- **WHEN** member `api` resolves to the default profile and its repo commits its own store binding
- **THEN** status shows `api` with its live-resolved store (the repo's, since repo wins) and the profile name it resolves to

#### Scenario: Orphaned sidecar
- **WHEN** the user removed a workset via `openspec workset remove` directly and runs `zpp workset doctor`
- **THEN** the orphaned sidecar is reported with a suggested cleanup command

#### Scenario: Shared-file member correspondence
- **WHEN** the `.zpp-workset` file has a `[members.X]` entry and `X` is not a member of the workspace
- **THEN** doctor reports the mismatch with a fix suggestion

#### Scenario: Multi-workset membership warns
- **WHEN** a repo is a member of two worksets
- **THEN** doctor warns, naming which workset's profile applies (alphabetically first) and which are shadowed

#### Scenario: Store member detection
- **WHEN** a member contains `.openspec-store/store.yaml`
- **THEN** status reports that member's role as a store without requiring a declaration
