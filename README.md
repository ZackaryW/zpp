# zpp — zack's project protocol

One CLI over the governance toolchain, with two jobs:

- **Wraps openspec** — worksets, the store registry, and governance resolution
  — to answer *which workset am I in, which store governs this repo, what is the
  effective config*. This is the only tool zpp calls at runtime.
- **Bootstraps and health-checks the rest** — `zpp bootstrap` installs the
  required toolchain (node, jq, ripgrep, uv/zmem, codegraph, the openspec CLI)
  and `zpp doctor` verifies each is present and sane. These are services zpp
  installs and checks, not libraries it wraps. saucepan is **optional**:
  bootstrap never fetches it and its absence never fails doctor — it is
  provisioned lazily on the first `zpp trait fetch`.

It never replaces any of them.

## Install

```sh
# uv is the sole prerequisite: https://docs.astral.sh/uv/
uv tool install zpp        # or from a checkout: uv tool install .
zpp bootstrap              # installs the rest of the toolchain (idempotent)
```

## Protocol rules

1. **Governance resolution, first hit wins.**
   A directory is (1) *self-governed* when a local `openspec/` root is in its
   ancestry; (2) *externally governed by committed fact* via `zpp.toml`
   (`[governance] store = "<id>"`); (3) *externally governed by personal view*
   via a workset sidecar binding; else (4) *ungoverned* — stated, not an
   error. Single-repo work self-governs with no governance repo required.
2. **Layout truth lives in the `.code-workspace`; zpp never writes it.**
   `import` adopts a workspace file (relative paths resolved against the
   file's own directory); `sync` is one-way reconciliation from it. Sharing
   and restoration = commit the workspace file, `zpp workset import` on the
   next machine. There is no export — the file already is the artifact.
3. **Workset config lives in profiles.** A workset holds named
   `[profiles.<name>]` blocks (zpp.toml-shaped). Every member resolves to
   `default` unless it points elsewhere (`profile = "<name>"`); a store
   binding is just `[governance] store` inside a profile — there is no
   separate bind command. Profiles live either in the machine-local sidecar
   (`~/.zpp/worksets/<name>.toml`, personal) or in a committed
   `<stem>.zpp-workset` file beside the `.code-workspace` (shared with
   collaborators, members referenced by **name only** so paths stay
   portable). When the shared file exists it wins entirely. Member *paths*
   are always machine-local (sidecar); the shared file never carries a path.
4. **Snapshots are a camera for zpp state only.** Auto-taken before every
   mutation; `restore` rewrites zpp-owned files, touching the user-owned
   workspace file only with `--workspace-file`. Not a backup, not a stash,
   not a distribution mechanism.
5. **Config layering**: repo `zpp.toml` → member's workset profile → the
   store's published `default` profile. Scalars override, lists union.
   **Default is a profile at every tier** — there is no `zpp.default.toml`:
   a store publishes by putting `[profiles.default]` (and others, with
   one-level `extends`) in its own `zpp.toml`; the top level of that file
   stays the store repo's self-config. zpp reads only its own protocol
   files — `pva.toml` stays with the legacy compose stack.
6. **Traits are queried in realtime — there is no composer.** Content comes
   from four sources with precedence `user > builtin > plugin > saucepan`
   (`~/.zpp/user/`, traits shipped in the package, agent-surface plugins, and
   `~/.zpp/saucepan/`); neither a remote pack nor a plugin can shadow shipped
   discipline. The `plugin` source is gathered **live** and only when you pass
   `--tool <surface>` (e.g. `--tool claude`), reading each installed plugin's
   `traits/` folder — no `--tool` means no plugin gathering, and nothing is
   cached to disk. Per-surface base dirs auto-resolve per OS, overridable via
   `[traits] plugins = { claude = "...", codex = "..." }`. Which traits
   *apply* comes from the config tiers (`[traits] apply`, lists union);
   `ZPP_TRAITS` replaces the personal tier for one session — committed tiers
   always survive.
7. **Governance tooling is user-level.** `.claude/` and peers are never
   committed (see `.gitignore`).
8. **Dogfood**: every zpp command is valid against the zpp repo itself — it
   is self-governed by its own local openspec root.

## Commands

```
zpp workset import <file.code-workspace> [--name ID] [--partial]
zpp workset sync <name> [--plan] [--yes]
zpp workset list|open|remove|status|doctor
zpp snapshot take|list|restore [--workspace-file]
zpp trait list [--tool T] [--json]   # every trait: source, shadowing, version
zpp trait show <name> [--tool T]     # one trait's content (winning source)
zpp trait effective [PATH] [--tool T] [--json]  # applied set, with tier provenance
zpp trait fetch <ref>                # fetch a remote pack via saucepan
zpp config resolve [PATH] [--sources] [--json]
zpp resolve [PATH] [--json]        # governance mode: which rule matched
zpp bootstrap [PATH] [--dry-run]   # install toolchain (config-aware)
zpp doctor [PATH] [--json]         # verify toolchain, detect-only, config-aware
```

`--json` is available wherever output matters to agents and skills.

## zpp-mcp — the Desktop chat surface

Governance mounts on Claude Code, Codex, and Kimi through session-start hooks.
The Claude **Desktop chat surface** has no hook — it is reached by registering
a local MCP server — so the `zpp-mcp/` workspace subproject serves the same
mount over stdio MCP:

- **Tools** (read-only, CLI-parity JSON): `resolve`, `trait_list`,
  `trait_effective`, `trait_content`, `doctor` — each a thin wrapper over
  `zpp.core`. No mutating operation is exposed.
- **Prompt** `zpp-governance` — composes the exact block `zpp-mount.sh` emits
  for the hook surfaces (header + effective traits, doctor only on
  degradation). It is the chat surface's stand-in for a session-start hook:
  user-invoked, so weaker than a hook, but the strongest that surface offers.

It is a **separate install** — `zpp` core stays typer + tomli-w; the MCP SDK
dependency lives only here:

```sh
uv tool install zpp-mcp     # provides the `zpp-mcp` stdio server
```

The `governance-of-agents-1v2` store ships a `claude_desktop_config.json`
snippet that registers this server (system-dependency posture — the store
carries no bundle, just the snippet). Every tool/prompt takes an explicit
`path` — the chat surface has no working directory.

The toolchain is configurable via a `[doctor]` section in the config tiers
(store → workset → repo, lists union): `exclude = ["<cmd>"]` removes builtin
tools from **both** doctor and bootstrap, and repeatable `[[doctor.more]]`
entries (`which = "<cmd>"`, `successnote = "<note>"`) add detect-only tools —
never installed by bootstrap; the note is shown when the tool is *present*, as
usage guidance. Broken config degrades to the builtin table with a warning.

## Development

```sh
uv sync --all-packages && uv run pytest    # workspace incl. zpp-mcp
uv run behave                              # BDD suite
uv run python scripts/bump.py minor        # bump zpp + zpp-mcp in lockstep, re-lock
```

`scripts/bump.py <patch|minor|major>` moves both workspace packages together
(they release as one) via `uv version` and re-locks. VS Code users get the
same as tasks (`.vscode/tasks.json` → **uv: bump version**, plus test/bdd/sync).

Governed by OpenSpec: see `openspec/` (this repo is self-governed — rule 1).
