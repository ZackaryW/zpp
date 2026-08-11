## 1. Feature contract

- [x] 1.1 Add fail-first feature scenarios for selected-home resolution, native home opening, and confirmed complete reset
- [x] 1.2 Cover reset preflight conflicts, absent integrations, removal failures, retry convergence, and preservation boundaries

## 2. Home command utilities

- [x] 2.1 Add selected-home and OpenLease-child path resolution with unsafe-boundary validation
- [x] 2.2 Add a shell-free native file-manager opener for the selected ZPP home
- [x] 2.3 Add fresh OpenLease-state preparation and exact-child replacement with rollback-safe behavior

## 3. Agent integration reset

- [x] 3.1 Extend the Agent Router adapter for user-scope skill and hook inspection
- [x] 3.2 Implement all-agent reset preflight and deterministic removal of intact ZPP-owned integrations
- [x] 3.3 Aggregate removal failures without replacing the prior OpenLease state and make retry converge

## 4. Public CLI wiring

- [x] 4.1 Change the root `--path` contract to select a ZPP home whose OpenLease state lives at `openlease/`
- [x] 4.2 Add `zpp open` with lazy home creation, native opening, and selected-path reporting
- [x] 4.3 Add `zpp reset --yes` with confirmation enforcement and no legacy overwrite option
- [x] 4.4 Preserve the existing init, resolve, behave, trait, and workflow command surfaces under the new home layout

## 5. Native BDD independence

- [ ] 5.1 Replace the workflow's mandatory `zpp.behave.yaml` path with native BDD execution and optional coordinated selection
- [ ] 5.2 Reconcile the BDD execution trait and capability feature with the corrected boundary

## 6. Acceptance and documentation

- [ ] 6.1 Pass the feature, unit, CLI, formatting, lint, and package-build verification suites
- [x] 6.2 Update the README for the default `~/.zpp` home, `--path`, `open`, and destructive reset boundaries
- [ ] 6.3 Form the canonical specifications and archive the completed OpenSpec change
