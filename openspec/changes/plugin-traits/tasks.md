# Tasks: plugin-traits

Discipline: fail-first BDD (behave) + TDD (pytest), same as workset-traits.
Scenario/unit FIRST (watch it fail), implementation SECOND (watch it pass).
Never write implementation before its failing scenario exists.

## 1. Resolver + extractor (BDD-first)

- [x] 1.1 Write `features/trait_plugins.feature`: tool-flag-folds-in-plugin-traits, no-tool-no-gathering, plugin-without-traits-folder-contributes-nothing, only-traits-extracted — confirm all fail
- [x] 1.2 Add an environment.py helper that builds a fake surface tree under a temp base (installed_plugins.json + a plugin shipping `traits/`, another shipping only `skills/`)
- [x] 1.3 Failing pytest units for `core/plugins.py`: ClaudeResolver base-dir selection per `platform.system()`, installed_plugins.json → installPath parsing, override precedence; shared Extractor reads `traits/*.md` only
- [x] 1.4 Implement `core/plugins.py` (ClaudeResolver, CodexResolver stub, shared Extractor) — units then scenarios green

## 2. Fold plugin source into resolution (BDD-first)

- [x] 2.1 Write feature scenarios for precedence: plugin-cannot-shadow-builtin, plugin-outranks-remote, same-name-within-plugin-tier-visible — confirm failing
- [x] 2.2 Failing pytest units for `core/traits.py` four-source precedence (`user > builtin > plugin > saucepan`) with plugin provenance
- [x] 2.3 Implement the `plugin` source in `core/traits.available()`/`content()` — gathered only when a tool is supplied; precedence and `tool/plugin` provenance — green

## 3. CLI --tool wiring (BDD-first)

- [x] 3.1 Write scenarios exercising `--tool` on `list`/`effective` (fold-in) and absence (unchanged) — confirm failing
- [x] 3.2 Thread a `--tool` option through `cli/trait.py` (`list`, `show`, `effective`); pass the gathered plugin source into the core query — green
- [x] 3.3 Update README trait section with `--tool`, the four-source precedence, and `[traits] plugins` override

## 4. Close-out

- [x] 4.1 Full suite green: `uv run behave` + `uv run pytest`; no scenario skipped
- [x] 4.2 Dogfood check: with the installed governance-of-agents plugin, `zpp trait list --tool claude` resolves it live (or, if it ships no `traits/` yet, contributes nothing without error) — record which
- [x] 4.3 Ground the Windows base dirs for Claude and Codex from authoritative docs; encode them in the resolvers with the config override retained; note any that remain unverified
- [x] 4.4 `openspec validate plugin-traits`; confirm every spec scenario maps to a behave scenario or pytest test
