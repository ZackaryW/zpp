# Design: plugin-traits

## Context

workset-traits established three trait sources (`user`, builtin, `saucepan`) with precedence `user > builtin > saucepan`, live realtime queries (`zpp trait list/show/effective`), and per-value tier provenance. This change adds a fourth source: agent-surface plugins.

Grounded on this machine: Claude's authority is `~/.claude/plugins/installed_plugins.json`, mapping `<plugin>@<marketplace>` → an `installPath` under `~/.claude/plugins/cache/…`, where each plugin's `plugin.json` declares a `skills`/content path. governance-of-agents is already installed there. Codex's `~/.codex/plugins/` exists but is sparsely populated with a different layout — confirming the two surfaces need distinct resolvers. openspec's own opener code already does platform-specific work (`PATHEXT`, `path.win32` vs `path.posix`), so per-OS branching is idiomatic in this ecosystem.

Owner decisions from the clarify interview are recorded as D1–D6 below.

## Goals / Non-Goals

**Goals:**

- Agent-surface plugins as a live, opt-in trait source, one surface per query.
- Deterministic four-source precedence with unshadowable builtin discipline.
- Platform divergence isolated to one resolver seam, with a config override backstop.
- Same fail-first BDD/TDD discipline as workset-traits.

**Non-Goals:**

- No populate command, no on-disk plugin-trait cache — gathering is live (D2).
- No flattening of plugin skills into traits — only an opt-in `traits/` folder is read (D1).
- No multi-surface gathering in one invocation — `--tool` names exactly one (D2).
- No changes to governance-of-agents-1 (it becomes a provider only when it ships `traits/`).
- No hardcoded Windows paths asserted from an unverifiable platform (D5).

## Decisions

### D1: Opt-in via a `traits/` folder; extractor reads `traits/*.md` only

A plugin is a workflow bundle (skills, scripts, manifests) — most of it is not trait content. A plugin declares trait intent by shipping a `traits/` directory; the extractor pulls only `traits/*.md` (name = filename stem). This keeps skills and traits distinct and means a plugin contributes nothing unless it opts in.

### D2: Live gathering gated by `--tool`, one surface per invocation

`--tool <surface>` on `zpp trait list/show/effective` folds that surface's plugin traits into the query, read live at that moment; without it, the `plugin` source is absent and behavior equals workset-traits. No populate step, no cache — consistent with the "queries are cheap, read live" thesis that removed the composer. Exactly one surface per invocation (no gather-all): the caller names the context, so "which plugin set am I seeing" is never ambiguous. Cost is bounded local file reads; if ever measured too high, a cache is an additive later change, not a design premise.

### D3: Resolver (per surface) + Extractor (shared)

- **Resolver** — one class per surface, single interface: resolve the surface's installed plugin roots. `ClaudeResolver` reads `installed_plugins.json` → `installPath` per plugin → the plugin's declared content path. `CodexResolver` reads Codex's own layout (thin until populated). Each resolver owns its per-OS base directory.
- **Extractor** — shared, surface-agnostic: given a resolved plugin root, read `traits/*.md`, tagging each trait with its `tool/plugin` origin.

Adding a surface or fixing a layout touches one resolver; the extractor and precedence never change. Mirrors the openspec-adapter isolation principle.

### D4: Precedence `user > builtin > plugin > saucepan`

Plugin traits are deliberately installed into the user's agent surface, so they outrank anonymous remote saucepan packs — but builtin discipline stays unshadowable by anything remote or plugin-supplied. Within the plugin tier, a same-named trait from a later-gathered plugin wins (last-write-wins across the ordered plugin list); provenance always names `tool/plugin`, so a collision is visible, never silent.

### D5: Cross-platform resolution, override as backstop

Each resolver branches on `platform.system()` for its base dir. Verified this machine: `~/.claude`, `~/.codex` on darwin/linux via `Path.home()`. Windows base dirs (candidates: `%APPDATA%`, `%LOCALAPPDATA%`, `%USERPROFILE%`) are **not** assertable from a macOS host; they are a grounding task at implementation (Claude/Codex docs or a Windows box) and until verified the config override is the escape hatch. `[traits] plugins = { claude = "<path>", codex = "<path>" }` — when present, the override wins over auto-detection. Stdlib only (`Path.home`, `os.environ`); no `platformdirs` dependency (ponytail rung 2).

### D6: BDD/TDD discipline

Built fail-first like workset-traits: behave scenarios in `features/trait_plugins.feature` drive the capability, pytest units cover resolver path selection and extraction; scenarios written RED before implementation. A fake plugin tree under the isolated `ZPP_HOME`/temp (installed_plugins.json + a plugin shipping `traits/`) exercises resolution without touching the real `~/.claude`.

## Risks / Trade-offs

- [Windows base paths unverifiable from this host] → resolver isolates the branch; paths grounded at implementation; config override backstops any wrong default (D5).
- [Live gathering does filesystem work per `--tool` query] → bounded local reads; consistent with the realtime thesis; cache is a later additive option, not now.
- [A plugin could ship a `traits/ponytail.md` attempting to shadow builtin discipline] → precedence forbids it (builtin > plugin); `trait list` marks the plugin copy shadowed.
- [installed_plugins.json / plugin.json shape is an upstream contract] → all format knowledge lives in `ClaudeResolver`; an upstream change touches one class, like the openspec adapter.
- [Codex layout is sparse/unstable today] → `CodexResolver` ships thin and honest; it resolves what exists and reports nothing rather than guessing.

## Open Questions

- Exact Windows base directories for Claude and Codex — resolve at implementation from authoritative docs; ship the override meanwhile.
- Whether `show --tool <surface>` should also gather (for symmetry) or whether plugin content is only meaningful through `list`/`effective` — default: `show` gathers too, so any listed trait is showable.
