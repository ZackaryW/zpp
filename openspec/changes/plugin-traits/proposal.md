# Proposal: plugin-traits

## Why

Claude and Codex are first-class agent surfaces, and each already hosts installed plugins that ship instruction fragments. Today those fragments are invisible to zpp — a plugin's discipline can only reach an agent through that plugin's own surface, never through zpp's trait system. Making agent-surface plugins a trait source turns anything the user has already installed into their agent tooling into governed, queryable traits — and it is the concrete bridge for the governance store: once governance-of-agents ships a `traits/` folder, its shards become available through zpp with no re-authoring.

## What Changes

- **New trait source: `plugin`** — a fourth source alongside user, builtin, and saucepan. A plugin opts in by shipping a `traits/` folder; only `traits/*.md` are read (skills, scripts, and manifests are ignored — a plugin is not automatically a trait).
- **Live, per-tool gathering gated by `--tool`**: `zpp trait list --tool claude` and `zpp trait effective --tool claude <path>` fold that one surface's plugin traits into the query, for that invocation only. Without `--tool`, no plugin gathering happens and behavior is unchanged. There is no populate command and no on-disk cache — resolution reads the installed plugins live each time.
- **Two abstractions**: a per-surface **Resolver** that owns per-OS base-directory resolution (branching on `platform.system()`), overridable per surface via `[traits] plugins = { claude = "...", codex = "..." }`; and a shared **Extractor** that reads `traits/*.md` from a resolved plugin root, namespacing each trait by `tool/plugin` for provenance.
- **Precedence extended to four sources**: `user > builtin > plugin > saucepan`. Plugin traits sit above anonymous remote packs but can never shadow shipped builtin discipline. Within the plugin tier, a same-named trait from a later gather wins; provenance always names the supplying `tool/plugin`.
- **Cross-platform resolution**: macOS/Linux base dirs (`~/.claude`, `~/.codex`) are verified; Windows paths are resolved by the same per-surface resolver and grounded at implementation, with the config override as the backstop for any platform whose default is wrong.

## Capabilities

### New Capabilities

<!-- none — this extends an existing capability -->

### Modified Capabilities

- `trait-system`: the source-precedence requirement changes from three sources to four (adding `plugin`); new requirements cover per-tool live gathering and the cross-platform resolver with per-surface override.

## Impact

- New code: `zpp/core/plugins.py` (per-surface resolvers + shared extractor); a `--tool` option threaded through `cli/trait.py` (`list`, `show`, `effective`); plugin folding in `core/traits.py`.
- New config: `[traits] plugins` overrides table.
- New tests: BDD scenarios in `features/trait_plugins.feature`, pytest units for resolver path selection and extraction.
- Sequencing: `trait-system` currently lives in the unarchived `workset-traits` change; this change's delta modifies that requirement, so `workset-traits` archives/syncs first.
- No change to governance-of-agents-1 in this change; it becomes a plugin trait provider only when it ships a `traits/` folder (a later, separate step).
