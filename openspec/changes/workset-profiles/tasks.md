# Tasks: workset-profiles

Discipline: fail-first BDD (behave) + TDD (pytest). Scenario/unit FIRST (watch
it fail), implementation SECOND (watch it pass).

## 1. Profiles model (BDD-first)

- [x] 1.1 Write `features/workset_profiles.feature`: default-profile-applies, explicit-pointer, repo-overrides-profile, dangling-pointer-warns — confirm failing
- [x] 1.2 Failing pytest units for the profiles model in `core/sidecar.py` (profile lookup per member, default resolution, empty tier on absence)
- [x] 1.3 Implement profiles in the sidecar schema and member resolution — green
- [x] 1.4 Remove `bind`/`unbind` (CLI + core + member `store` field); rewrite the existing bind-based scenarios/units to profile form

## 2. Resolution rewiring (BDD-first)

- [x] 2.1 Extend scenarios: profile-supplies-rule-3-binding, committed-beats-profile, profile-is-middle-config-tier, profile-traits-reach-members — confirm failing
- [x] 2.2 Failing units for `core/governance.py`: rule 3 from resolved profile; middle tier = member profile (membership lookup, not binding lookup)
- [x] 2.3 Implement profile-sourced resolution and config tier — green; `ZPP_TRAITS` still replaces the workset tier

## 3. Shared .zpp-workset file (BDD-first)

- [x] 3.1 Write scenarios: shared-file-wins-over-sidecar, names-only-portability (import in a relocated folder), personal-fallback, sync-never-touches-the-file — confirm failing
- [x] 3.2 Failing units for shared-file loading (name pairing with the .code-workspace, members-by-name validation)
- [x] 3.3 Implement shared-file detection and precedence — green

## 4. Status, doctor, close-out

- [x] 4.1 Scenarios: status-shows-live-resolution-and-profile-and-home, multi-workset-warns-with-winner — confirm failing, then implement
- [x] 4.2 Full suites green; behave --dry-run integrity clean
- [x] 4.3 Dogfood: a `.zpp-workset` beside a real workspace file resolves the same profiles after folder relocation
- [x] 4.4 Update README (profiles, .zpp-workset, removed bind commands); `openspec validate workset-profiles`

## 5. Folded in during apply (owner directives)

- [x] 5.1 Profile `extends` (one level): RED scenario + unit, then implement in sidecar.profile_config
- [x] 5.2 Doctor shared-file member correspondence check: RED scenario + unit, then implement
- [x] 5.3 Remove zpp.default.toml: store tier = the store's published [profiles.default] in its own zpp.toml; rewrite fixtures RED, implement _store_published/_repo_tier, README + deltas updated
