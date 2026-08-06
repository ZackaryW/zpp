## Why

ZPP workflow guidance can currently misclassify repository-environment tooling as product behavior and can interpret a monorepo's multiple legitimate subprojects as one invalid feature surface. The recent version-bump attempt demonstrated both risks: environmental tooling was incorrectly promoted into product OpenSpec and BDD, while multi-subproject feature ownership remained underspecified.

## What Changes

- Make `zpp-clarify-change` classify each requested outcome as repository-environment/tooling, shipped source/product behavior, or a mixed request before it lists, selects, or creates product OpenSpec work.
- Keep environmental-only work outside product capability deltas, Gherkin, and canonical product specifications; split mixed requests so only shipped behavior enters the product workflow.
- Make `zpp-shape-feature` identify justifiably affected monorepo subprojects from established repository boundaries and shape features in each subproject's native feature surface without requiring one root, framework, or runner.
- Add a standalone dependency-free `uv run scripts/bump_version.py <X.Y.Z>` repository tool outside `src/zpp`; cover it with native script tests and no new product BDD.
- Use the environmental script to synchronize the already-selected project release into `src/zpp/__init__.py`, then update only the existing source-level product identity expectation from `0.9.5` to `0.9.6`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Clarification must classify environmental versus shipped behavior before product bootstrap, and feature shaping must preserve justified monorepo subproject boundaries.
- `global-bootstrap-and-agent-setup`: Reconcile the existing product identity contract with the already-selected `0.9.6` release.

## Impact

Affects two packaged workflow skills, their installed-skill contract coverage, the existing version identity expectation, a standalone repository script and focused tests, README development guidance, and runtime version metadata. The bump script itself is environmental and deliberately absent from capability deltas and Gherkin.

## Unresolved — Do Not Assume

None. Classification follows observable outcome rather than filename alone: packaged workflow skills under `src/zpp/artifacts` are shipped source behavior, while the standalone maintainer script is repository-environment tooling.
