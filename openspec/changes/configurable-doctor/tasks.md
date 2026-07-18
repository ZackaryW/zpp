# Tasks: configurable-doctor

Discipline: fail-first BDD (behave) + TDD (pytest). Scenario/unit FIRST (watch
it fail), implementation SECOND (watch it pass).

## 1. Config-driven table (BDD-first)

- [x] 1.1 Write `features/doctor_config.feature`: excluded-tool-neither-checked-nor-installed, store-tier-union, degraded-resolution-warns — run behave, confirm all fail
- [x] 1.2 Failing pytest units for `_effective_tools(path)`: exclude filtering, tier union, builtin fallback on resolution failure
- [x] 1.3 Implement config-aware table assembly in `core/toolchain.py`; thread `[PATH]` through `zpp doctor` / `zpp bootstrap` in `cli/root.py` — green

## 2. Detect-only more-tools (BDD-first)

- [x] 2.1 Extend the feature file: present-more-shows-successnote, missing-more-plain-and-nonzero, bootstrap-ignores-more — confirm failing
- [x] 2.2 Failing pytest units for `[[doctor.more]]` mapping (detect_only entries, note surfacing)
- [x] 2.3 Implement more-entry handling in doctor (successnote on present) and bootstrap (skip entirely) — green

## 3. Close-out

- [x] 3.1 Full suite green: `uv run behave` + `uv run pytest`; existing doctor/bootstrap-agreement tests still pass against the effective table
- [x] 3.2 Dogfood: add `[[doctor.more]] which = "git"` (successnote pointing at the zmem commit grammar) to zpp's own `zpp.toml`; `zpp doctor` shows it green with the note
- [x] 3.3 Update README doctor/bootstrap lines with `[PATH]` and the `[doctor]` section
- [x] 3.4 `openspec validate configurable-doctor`; confirm every spec scenario maps to a behave scenario or pytest test
