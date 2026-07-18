# Tasks: workset-traits

Discipline: fail-first BDD (behave) + TDD (pytest). Every feature task pair is
scenario/test FIRST (watch it fail), implementation SECOND (watch it pass).
Never write implementation before its failing scenario exists.

## 1. Discipline declaration

- [x] 1.1 Create `zpp.toml` at the repo root declaring `[tdd] stack = "python"` and `[bdd] stack = "python"`
- [x] 1.2 Add behave as a dev dependency (`uv add --dev behave`); verify `uv run behave --version`
- [x] 1.3 Scaffold `features/environment.py` with an isolated `ZPP_HOME` per scenario and a fake-saucepan hook

## 2. Trait sources and precedence (BDD-first)

- [x] 2.1 Write `features/trait_sources.feature`: scenarios for user-shadows-builtin, remote-cannot-shadow-builtin, builtin-discipline-set-present, unknown-trait-warns — run behave, confirm all fail
- [x] 2.2 Failing pytest units for `core/traits.py` source scan + precedence merge
- [x] 2.3 Implement `core/traits.py`: source dirs (`~/.zpp/user`, packaged builtins, `~/.zpp/saucepan`), precedence `user > builtin > saucepan`, shadow reporting — units then scenarios green
- [x] 2.4 Ship builtin trait files in the package (`zpp/traits/`: ponytail, structure, coverage, commit-stage — content ported from governance shards); wheel data verified by a scenario

## 3. Realtime query surface (BDD-first)

- [x] 3.1 Write `features/trait_query.feature`: list-with-source-and-shadowing, show-content, effective-concatenation-in-tier-order, effective-json-provenance — confirm failing
- [x] 3.2 Failing pytest units for effective-set computation (tier union order)
- [x] 3.3 Implement `[traits] apply` tier resolution in `core/governance.py` reuse + `cli/trait.py` (`list`/`show`/`effective`, `--json`) — green
- [x] 3.4 Update README command reference with the `zpp trait` group

## 4. Session env override (BDD-first)

- [x] 4.1 Write `features/trait_env.feature`: env-replaces-workset-tier-only, committed-tiers-survive, provenance-says-env, typo-warns — confirm failing
- [x] 4.2 Implement `ZPP_TRAITS` handling in the tier resolution — green

## 5. saucepan adapter and managed mode (BDD-first)

- [x] 5.1 Write `features/trait_remote.feature` (fake saucepan binary via environment.py): managed-fetch-on-first-use-reports-explicitly, system-mode-never-installs, remote-pack-traits-listed-with-version — confirm failing
- [x] 5.2 Failing pytest units for `core/sauce.py` adapter (JSON parsing, exit codes, managed-binary path selection)
- [x] 5.3 Implement `core/sauce.py`: managed release fetch to `~/.zpp/bin/` (pinned after first fetch), system-mode PATH requirement, pack scan into the saucepan source — green
- [x] 5.4 Add saucepan to the toolchain table with mode awareness; extend `zpp doctor` to report mode + binary provenance; unit-test doctor/bootstrap agreement stays intact

## 6. Close-out

- [x] 6.1 Full suite green: `uv run behave` + `uv run pytest`; no scenario skipped
- [x] 6.2 Dogfood check: in this repo, `zpp trait effective` serves the builtin discipline set for a session with `ZPP_TRAITS=ponytail,structure`
- [x] 6.3 `openspec validate workset-traits`; confirm every spec scenario maps to a behave scenario or pytest test
