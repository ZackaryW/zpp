## 1. Assignment record

- [x] 1.1 Extend the sidecar schema in `zpp/core/sidecar.py` with the
      reference-store assignment record, bumping `version` from 2 and
      tolerating sidecars written before the bump
- [x] 1.2 In `zpp/core/worksets.py`, add assign and unassign operations that
      validate the store id against `adapter.store_list()` read-only and
      refuse an unknown id without touching the registry

## 2. Surfaces

- [x] 2.1 Add `zpp workset assign-store` / `unassign-store` in
      `zpp/cli/workset.py`. Listing is served by `workset status` rather than
      a third command, which would only restate it
- [x] 2.2 Report assigned reference stores (id and root) in
      `governance.resolve()` output, distinct from the governing store and
      empty when there are none
- [x] 2.3 Render them in `zpp resolve` human output (`zpp/cli/root.py`) under
      a heading that cannot be read as the governing store
- [x] 2.4 Include assignments in `zpp workset status`

## 3. Doctor

- [x] 3.1 In `worksets.doctor()`, report an assigned reference store whose id
      is unregistered or whose root path is missing, with a fix suggestion;
      emit nothing for healthy assignments

## 4. Verification

- [x] 4.1 Unit tests: assignment round-trip, unknown id refused, non-member
      assignment accepted, doctor anomaly vs healthy silence, sidecar version
      migration
- [x] 4.2 Test that resolution is unchanged by assignment — mode, rule, store,
      effective root, and isolation state identical before and after
- [x] 4.3 BDD scenarios cover the refusal paths (registry unreachable → fails
      closed with nothing written; unknown assignment refused). Accepting an
      assignment needs a genuinely registered store, which the hermetic behave
      environment cannot create without a test-only seam the suite
      deliberately avoids — the unit suite covers acceptance
- [x] 4.4 Confirm the at-most-one-dedicated-store tests still pass untouched
      (`tests/test_worksets.py`, `tests/test_governance.py`)
- [x] 4.5 Run the full suite and `openspec validate --strict`
- [ ] 4.6 Commit on the decision branch via the zmem grammar; merge to `main`
      without squashing before close-out
