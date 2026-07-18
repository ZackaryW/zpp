# Proposal: workset-traits

## Why

Agent instructions today are compiled artifacts: shards bundled by presets, concatenated by compose.py into agent files that drift from their sources and require a build step per change. Trait queries are cheap enough to serve in realtime — so the composer concept can be dropped entirely. zpp already owns the tier resolution (store → workset sidecar → repo) that decides *which* fragments apply; what's missing is trait *content* sources (local, builtin, remote) and a live query surface agents consume directly. This also completes the dogfood rule: with the generic discipline shards shipped as zpp builtins, zpp's own agent sessions govern themselves through zpp.

## What Changes

- **Composer dropped.** No compiled agent files, no composition step — agents query traits in realtime via a new `zpp trait` command group: `list` (available traits with source + version), `show <name>` (one trait's content), `effective [path]` (the applied set for a context, concatenated, `--json` with provenance).
- **Three trait content sources**, collision precedence `user > builtin > saucepan`:
  - `~/.zpp/user/` — user-registered trait files;
  - **builtin** — the generic discipline set (`ponytail`, `structure`, `coverage`, `commit-stage`) shipped inside the zpp package, moved from the governance store's shards so zpp self-manages;
  - `~/.zpp/saucepan/` — remote trait packs fetched by saucepan (name-based refs; sources declared centrally, not inside refs).
- **saucepan integration in managed mode by default**: zpp fetches the saucepan release binary to `~/.zpp/bin/` on first use; `[traits] saucepan = "system"` opts into PATH-provided instead. Remote sources can never shadow builtin names (precedence is the hijack guard).
- **Trait application tiers** (which traits are active): store defaults → workset sidecar overlay → repo `zpp.toml`, lists union — with `ZPP_TRAITS` as a per-session env override that **replaces the workset tier only**; committed tiers always survive, so discipline traits belong in store/repo config.
- **BDD/TDD discipline declared and followed**: `zpp.toml` at the repo root declares `[tdd] stack = "python"` and `[bdd] stack = "python"`; behave scenarios in `features/*.feature` drive this capability fail-first (and feed zmem's graph); pytest remains the unit layer.

## Capabilities

### New Capabilities

- `trait-system`: trait content sources and precedence, realtime query surface (`list`/`show`/`effective`), application tiers with the `ZPP_TRAITS` session override, and saucepan-backed remote packs.

### Modified Capabilities

- `environment-bootstrap`: gains the managed/system tool-mode requirement — saucepan joins the toolchain as a release binary that zpp may self-manage under `~/.zpp/bin/` instead of requiring it on PATH.

## Impact

- New code: `zpp/core/traits.py` (sources, precedence, effective-set), `zpp/core/sauce.py` (saucepan adapter, managed-binary fetch), `zpp/cli/trait.py`; `[traits]` config section.
- New machine-local state: `~/.zpp/user/`, `~/.zpp/saucepan/`, `~/.zpp/bin/`.
- Packaged data: builtin trait markdown files inside the zpp wheel.
- New repo files: `zpp.toml` (`[tdd]`/`[bdd]` declarations), `features/*.feature`, behave as a dev dependency.
- External: saucepan release binary (GitHub releases); governance-of-agents-1 unchanged this round (its shards remain until it adopts zpp traits).
