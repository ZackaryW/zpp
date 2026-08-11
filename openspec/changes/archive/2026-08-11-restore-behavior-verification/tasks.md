## 1. Contract tests and core behavior

- [x] 1.1 Add fail-first tests for the closed version-one mapping, repository-safe path/glob validation, ordered targets, gates, and conservative affected-target selection.
- [x] 1.2 Implement behavior models, mapping validation, and deterministic selection in `zpp.core`.
- [x] 1.3 Add fail-first tests for mutually exclusive complete, exact-target, gate, default affected, and paired-revision operation inputs and reports.
- [x] 1.4 Implement the core behavior operation service and preserve no-target outcomes without starting a provider.

## 2. Provider and repository utilities

- [x] 2.1 Add fail-first tests for repository-root discovery, repository path normalization, and full-match behavior globs.
- [x] 2.2 Implement the required Git, path, and glob utilities under `zpp.utils` using current OpenLease public adapters where applicable.
- [x] 2.3 Add fail-first tests for the explicit adapter registry, shell-free argv expansion, Nx discovery and surface validation, Go Task discovery and surface validation, and fail-closed provider behavior.
- [x] 2.4 Implement `argv`, `nx`, and `go-task` adapters plus provider diagnostics under `zpp.utils` without dynamic adapter discovery or installation behavior.

## 3. OpenLease extension and public CLI

- [x] 3.1 Add fail-first tests for dedicated YAML direct binding, exact bounded initialization, independent `zpp.behave` registration, and no-space CLI operation.
- [x] 3.2 Extend the existing OpenLease utility to register and invoke `zpp.behave` beside `zpp.traits`, including direct initialization and execution.
- [x] 3.3 Add fail-first tests that the agent-native trait hook starts no behavior operation and that registered callbacks remain inert until explicitly selected.
- [x] 3.4 Implement callback-time direct reopening of the exact repository behavior document from real OpenLease repository or cohort context, without managed callback configuration, temporary repositories, or additional spaces.
- [x] 3.5 Add fail-first CLI tests for `zpp behave init`, `zpp behave COMMAND`, every selection option, validation errors, output forwarding, no-target reporting, and provider exit-code propagation.
- [x] 3.6 Implement the restored root `behave COMMAND` surface in `zpp.cli` and register it in the stable application hierarchy.

## 4. Workflow integration and acceptance

- [x] 4.1 Add fail-first artifact tests for `bdd-execution` modes, `zpp-workflow` gate identity, affected fallback, and absence of legacy gate migration.
- [x] 4.2 Reconcile the packaged `bdd-execution` trait and consolidated workflow skill so advisory policy drives only explicit repository-declared behavior verification.
- [x] 4.3 Port representative version-one behavior configuration fixtures and verify they validate and execute without structural rewriting.
- [x] 4.4 Run focused behavior, CLI, OpenLease, and artifact tests, then the complete test and lint suites.
- [x] 4.5 Build the ZPP 2.0 distribution and verify the wheel contains behavior runtime modules, the consolidated workflow skill, and reconciled trait artifacts.
