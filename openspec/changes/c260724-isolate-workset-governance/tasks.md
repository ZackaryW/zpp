## 1. Contract and Test Fixtures

- [x] 1.1 Add fail-first unit and behavior fixtures for zero/one/multiple store members, distinguishing `.openspec-store/store.yaml` from ordinary local `openspec/` roots
- [x] 1.2 Add Git fixtures for exact-path members, linked worktrees, independent clones with normalized remotes, missing remotes, and ambiguous remote matches
- [x] 1.3 Define and test the JSON shapes for logical member aliases, effective governance context, provisioning-required failures, invalid-workset failures, and lease state

## 2. Workset Identity and Cardinality

- [x] 2.1 Implement dedicated-store enumeration and reject multi-store import before creating OpenSpec or sidecar state
- [x] 2.2 Extend sync planning to detect multi-store results before mutation and add doctor repair findings for legacy violations
- [x] 2.3 Implement exact-path-first logical member resolution with Git common-directory and normalized-remote fallback plus explicit member override

## 3. Effective Governance Resolution

- [x] 3.1 Implement default-branch discovery from the dedicated store's `origin/HEAD` and derived branch naming as `<member>/<project-branch>`
- [x] 3.2 Extend governance/config resolution with registered base root, effective branch/root, member, project branch, and structured fail-closed states
- [x] 3.3 Verify read-only commands create no files, branches, worktrees, views, registry changes, or leases across success and failure paths
- [x] 3.4 Add `cYYMMDD-<descriptive-name>` validation and numeric-leading-id guidance

## 4. Provisioning and Session Views

- [x] 4.1 Add an idempotent provisioning core that preflights branch/base/checkout overrides and creates or reuses governance worktrees only under validated zpp-owned paths
- [x] 4.2 Add `workset open` inputs for current/explicit project checkout and manual member, branch, base, and existing-checkout overrides
- [x] 4.3 Implement zpp-owned branch session views through the OpenSpec adapter without rewriting `.code-workspace` or writing OpenSpec data directly
- [x] 4.4 Add cleanup, status, and doctor handling for generated session views, including interrupted provisioning and rollback tests

## 5. Governance Leases

- [x] 5.1 Implement canonical lease keys and machine-local shared-read/exclusive-write acquisition, renewal, upgrade, and release
- [x] 5.2 Add live-holder diagnostics, expiry classification, and explicit stale-lease recovery without silent lease stealing
- [x] 5.3 Cover concurrent readers, conflicting writers, isolated-branch writers, crashed sessions, and idempotent release with deterministic tests

## 6. Integration and Release

- [x] 6.1 Update CLI help, README protocol rules, workset status/doctor output, and migration guidance for automatic single-store isolation
- [x] 6.2 Add integration tests that expose the effective-root and lease contract required by `c260724-promote-governance-specs`
- [x] 6.3 Run the full unit/BDD suite, `openspec validate`, packaging checks, and a clean install smoke test before coordinating the zpp release with governance-of-agents-1v2
