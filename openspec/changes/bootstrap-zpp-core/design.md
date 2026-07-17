# Design: bootstrap-zpp-core

## Context

The governance ecosystem today: openspec (Node CLI) owns stores, changes, specs, and personal worksets; zmem (Python/uv) owns per-repo memory; codegraph (binary) owns code intelligence; agent-compose (compose.py) owns shard composition and, incidentally, pva config resolution; ~30 duplicated `.sh`/`.ps1` scripts own setup, doctor, and build steps.

Findings from the exploration session that constrain this design:

- openspec resolution is: ancestor-walk for a local `openspec/` root, else explicit `--store <id>` against the machine registry (`~/.local/share/openspec/stores/registry.yaml`). There is **no project→store binding mechanism** — that gap is zpp's core territory.
- `openspec workset` stores state in `~/.local/share/openspec/worksets/worksets.yaml` with **strict zod schemas** — extra keys make openspec reject the file. zpp cannot extend workset storage in-place; a sidecar is forced.
- Worksets have no import: `.code-workspace` files are generated, disposable artifacts. Members are bare `{name, path}` with no semantics.
- Workset doctrine is "purely local, never committed, nothing written into member folders" — zpp's sidecar inherits this.
- `openspec workset create/list` support `--json`; that CLI surface is the integration point, not file scraping (files are read-only fallback).

## Goals / Non-Goals

**Goals:**

- **Dogfood rule**: a successful project utility manages its own project — every zpp command must be valid against the zpp repo itself (it is self-governed by its local openspec root).
- **User-level governance rule**: `.claude/` (and peer agent-tooling directories) are never committed; governance tooling is set up at user level. The repo `.gitignore` enforces this.
- One cross-platform Python codebase replacing the duplicated shell scripts (bootstrap, doctor).
- Authoritative, queryable answers to: which workset am I in, which store governs this repo, what is the effective config, which governance mode applies.
- `.code-workspace` as the portable, user-owned layout truth; zpp adopts and follows it.
- Local snapshot/undo of zpp's own state.

**Non-Goals:**

- Reimplementing openspec (changes, specs, stores, workset composition/opening) — zpp wraps.
- Reimplementing zmem or codegraph.
- Snapshotting repo contents or SHAs — snapshot covers zpp config state only; git owns code history.
- Two-way `.code-workspace` sync — zpp never writes the workspace file.
- Retiring governance-of-agents-1 scripts in this change (later, after parity is proven).
- Team-shared sidecars or any server component.

## Decisions

### D1: Python on uv, not Rust

The workload is orchestration (TOML/JSON resolution, tool checks, subprocess calls) — Rust buys nothing user-visible. The ecosystem is already Python (zmem, compose.py) so logic can be imported, not ported across a boundary. `uv tool install zpp` gives isolated, pinned, cross-platform distribution; uv fetches the interpreter itself. Bootstrap paradox resolved: uv is the sole manual prerequisite (one curl/scoop command); an optional ~10-line `bootstrap.{sh,ps1}` shim is the only shell that survives.

Alternative considered: Rust static binary — rejected for iteration cost and forced reimplementation of Python-resident logic.

CLI framework: **typer**. Command groups map to nested Typer apps (`workset`, `snapshot`, `config` as sub-apps mounted on the root app; `bootstrap`, `doctor`, `resolve` as root commands), which mirrors the protocol's structure one-to-one and gives completion/help for free.

Package layout — three subpackages by responsibility, one CLI file per command group:

```
zpp/
├── core/    # domain logic: adapter, sidecar, worksets, governance, snapshot, toolchain
├── utils/   # pure helpers: paths (~/.zpp layout), workspace (JSONC reader)
└── cli/     # typer wiring only: __init__ (root app), workset, snapshot, config, root, common
```

`cli/` holds no domain logic (presentation + error mapping only); `core/` never imports typer; `utils/` imports nothing from zpp. The entry point stays `zpp.cli:app`.

### D2: Wrap openspec workset; identity is shared by name

`zpp workset <name>` IS `openspec workset <name>` plus a sidecar keyed by the same name. zpp delegates create/open/remove/list to the openspec CLI (`--json` where available) and never writes openspec-owned files. zpp inherits openspec's naming rules (kebab-case) as a protocol commitment.

Alternative considered: independent "project" concept — rejected; a parallel registry that can disagree with worksets is worse than none, and the 1:1 naming removes a permanent "is project X the same as workset X?" tax.

### D3: Sidecar layout

```
~/.zpp/
├── worksets/<name>.toml          # per-workset sidecar
└── worksets/<name>/snapshots/    # local snapshots
```

Sidecar content: source `.code-workspace` path (for sync), member metadata keyed by member name (store binding, detected role), optional project-scoped pva overlay. Machine-local and personal by doctrine; never committed, never written into member folders.

### D4: `.code-workspace` is layout truth; import/sync are one-way

- `import <file.code-workspace>`: parse JSONC, resolve relative folder paths against the file's own directory (VSCode semantics), create the openspec workset with absolute paths, write the sidecar recording the source file path.
- `sync [name]`: re-read the recorded source file, reconcile layout drift into the workset and sidecar. Folder `name` labels are the stable keys for migrating member metadata; a rename without a `name` label is indistinguishable from remove+add, so sync presents its reconciliation plan before applying destructive metadata changes.
- zpp never writes the `.code-workspace`. Sharing/restoration = commit the workspace file, `zpp workset import` on the next machine. No export command — the file already is the artifact.

Alternative considered: canonical zpp file with workspace export (workset's own model) — rejected; it recreates the two-files-drift problem and kills "free import" of existing workspace files.

### D5: Four-mode governance resolution, first hit wins

1. Local `openspec/` root in ancestry → **self-governed** (openspec's native rule adopted as rule 1; single-repo work needs no governance repo).
2. In-repo `zpp.toml` binding (`[governance] store = "<id>"`) → **externally governed, committed fact**.
3. Workset sidecar binding → **externally governed, personal view**.
4. None → **ungoverned**, stated explicitly.

Repo-level binding (rule 2) is truth about the repo; the sidecar (rule 3) is truth about a personal view. `doctor` flags disagreements between them rather than silently preferring one. Store references are validated against openspec's registry (read-only); a "local root" and a "registered store" are distinguished on disk (`openspec/` dir vs `.openspec-store/store.yaml` + registry entry).

### D6: Config resolution layering

`zpp config resolve` computes: governed repo `zpp.toml` → workset sidecar overlay → governing store `zpp.default.toml`. Scalars override, lists union (pva's merge semantics, verified identical to `pva_config.merge_section`). zpp reads only its own protocol files: `pva.toml`/`pva.default.toml` remain the legacy compose stack's files, untouched and unread by zpp, avoiding two tools with dialects of one file. A store publishes `zpp.default.toml` when it adopts zpp; compose.py becomes a consumer of zpp's resolution when it migrates (out of scope here).

### D7: Snapshot = local undo of zpp state only

`take` copies the sidecar plus the current text of the source `.code-workspace` into `snapshots/<timestamp>/`; auto-`take` runs before every mutating command (import, sync, bind, config edits). `restore` rewrites only zpp-owned files — restoring the workspace-file copy requires an explicit flag since that file is user-owned. Snapshot never touches member repos; it is a camera for config, not a stash, not a backup, not a distribution mechanism.

### D8: Bootstrap/doctor as data-driven check/install pairs

One table of tools (node, jq, rg, uv-hosted zmem, codegraph, openspec CLI, global openspec assets), each with a detect predicate and per-OS install strategy. `doctor` runs detect-only and reports one line per tool; `bootstrap` runs detect→install idempotently. This mirrors setup.sh/pv-doctor behavior from a single cross-platform codebase.

## Risks / Trade-offs

- [openspec has no hooks; direct `openspec workset remove` orphans sidecars] → `zpp workset doctor` detects orphaned sidecars, worksets without sidecars, and dead member paths; wrap-commands clean up when used.
- [Worksets are an experimental openspec surface ("slice 7.1", attach-dirs kill switch active)] → all openspec interaction isolated behind an adapter module; format is versioned and zod-validated so breakage is loud; only the adapter changes on upstream reshape.
- [Hand-edits or VSCode UI edits mangle the `.code-workspace` or sidecar] → auto-snapshot before mutations; `snapshot restore` recovers; sync shows a plan before destructive reconciliation.
- [Rename-vs-remove ambiguity in sync when folders lack `name` labels] → plan-before-apply plus protocol guidance to label folders; metadata for removed members is retained in the snapshot taken before sync.
- [Two binding layers (repo fact vs sidecar view) can disagree] → resolution order is deterministic and doctor surfaces the conflict; zpp never silently merges them.
- [JSONC parsing of `.code-workspace`] → use a tolerant JSONC parser; never rewrite the file, so round-trip fidelity is not required.

## Open Questions

- Does `zpp bootstrap` also install the global `~/.claude` OpenSpec assets (setup.sh does today), or is that openspec's own `init` territory now?
- Snapshot retention policy (count-based prune vs keep-all) — trivial either way, decide during implementation.
- Whether `zpp workset open` needs to exist at all versus documenting `openspec workset open` (lean answer: thin passthrough for one-front-door ergonomics).
