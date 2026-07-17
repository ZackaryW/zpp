# Tasks: bootstrap-zpp-core

## 1. Package scaffold

- [x] 1.1 Create `pyproject.toml` (uv-managed, Python 3.11+ floor for tomllib) with a `zpp` console entry point and typer as the CLI framework
- [x] 1.2 Create the package skeleton: `zpp/cli.py` (root typer app; `workset`, `snapshot`, `config` sub-apps; top-level `bootstrap`, `doctor`, `resolve` commands), `zpp/paths.py` (`~/.zpp/` layout resolution)
- [x] 1.3 Set up test harness (pytest) with a tmp-dir fixture that isolates `~/.zpp/`, openspec data dirs, and fake repos

## 2. openspec adapter

- [x] 2.1 Implement the openspec adapter module: subprocess wrappers for `openspec workset create/list/open/remove --json` and `openspec store list --json`, with typed results and loud failures
- [x] 2.2 Implement read-only registry access (store registry file) and on-disk detection helpers: local `openspec/` root ancestor walk, `.openspec-store/store.yaml` presence
- [x] 2.3 Adapter tests against fixture file trees (no real openspec install required; subprocess calls faked)

## 3. Workset import and sidecar

- [x] 3.1 Implement tolerant JSONC parsing of `.code-workspace` files and relative→absolute folder resolution anchored at the file's directory
- [x] 3.2 Implement the sidecar model (`~/.zpp/worksets/<name>.toml`): source workspace path, members keyed by name with binding/role fields, project-scoped pva overlay section; atomic writes
- [x] 3.3 Implement `zpp workset import`: validations (name rules, collisions, missing folders with explicit partial-import flag), delegate creation to the adapter, write sidecar
- [x] 3.4 Implement `zpp workset bind` with registry validation and error listing registered stores

## 4. Sync

- [x] 4.1 Implement layout diffing between the workspace file and current workset/sidecar (added, removed, renamed-by-label, path-changed members)
- [x] 4.2 Implement the reconciliation plan display and confirmation gate for metadata-destructive changes; apply path recreates the openspec workset and migrates sidecar metadata by member name
- [x] 4.3 Sync tests: folder added, labeled rename preserves bindings, unlabeled replace requires confirmation, source file missing

## 5. Snapshots

- [x] 5.1 Implement `zpp snapshot take/list/restore`: snapshot dir layout with timestamp + trigger provenance; restore scoped to zpp-owned files, explicit flag for workspace-file writeback
- [x] 5.2 Wire auto-snapshot into every mutating command (import, sync, bind, remove, config edits)
- [x] 5.3 Snapshot tests: auto-take before sync, default restore leaves `.code-workspace` untouched, explicit flag writes it back

## 6. Governance resolution and config

- [x] 6.1 Implement four-mode resolution (local root → repo pva.toml → sidecar binding → ungoverned) returning mode, store id, and matched rule; dangling-store warnings
- [x] 6.2 Implement `zpp config resolve`: repo → sidecar overlay → store default layering with scalar-override/list-union semantics, JSON output, per-value source attribution; verify behavior matches compose.py's resolution on the governance-of-agents-1 fixtures
- [x] 6.3 Resolution tests: each mode, committed-binding-beats-sidecar, self-governed config layering

## 7. Status and doctor (workset)

- [x] 7.1 Implement `zpp workset status`: members, governance modes, bindings, detected store roles, source file
- [x] 7.2 Implement `zpp workset doctor`: orphaned sidecars, worksets without sidecars, dead member paths, moved source files, dangling store bindings — each with a suggested fix
- [x] 7.3 Doctor tests covering each drift class

## 8. Environment bootstrap and doctor

- [x] 8.1 Define the toolchain table (node, jq, rg, zmem-via-uv, codegraph, openspec CLI) with detect predicates and per-OS install strategies, ported from setup.sh/pv-doctor checks
- [x] 8.2 Implement `zpp doctor` (detect-only, one line per tool) and `zpp bootstrap` (idempotent install, manual-step fallthrough with distinct exit status)
- [x] 8.3 Tests with faked PATH/subprocess: doctor/bootstrap agreement, idempotent re-run, partial installability exit status

## 9. Close-out

- [x] 9.1 Write README: protocol rules (four modes, layout-truth-in-workspace-file, sidecar doctrine, snapshot scope), command reference, uv install instructions
- [x] 9.2 End-to-end smoke test on this machine: import a real `.code-workspace` composing governance-of-agents-1 + a governed repo, bind, status, sync, snapshot restore
- [x] 9.3 Validate the change (`openspec validate bootstrap-zpp-core`) and confirm all specs' scenarios have test coverage
