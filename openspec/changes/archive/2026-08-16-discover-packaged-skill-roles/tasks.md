## 1. Restructure packaged skills into roles

- [x] 1.1 Move `src/zpp/artifacts/skills/zpp-workflow/` to `src/zpp/artifacts/skills/workflow/zpp-workflow/` preserving history
- [x] 1.2 Move `zpp-configure-behave/` and `zpp-author-trait/` to `src/zpp/artifacts/skills/companion/` preserving history
- [x] 1.3 Confirm a built wheel contains every file under both role directories

## 2. Prove discovery behavior fail-first

- [x] 2.1 Add a failing unit test that the companion role is discovered in deterministic sorted order, independent of creation order
- [x] 2.2 Add a failing unit test that a role entry without `SKILL.md` is ignored while valid siblings still load
- [x] 2.3 Add a failing unit test that an invalid packaged skill document fails the whole load rather than yielding a partial inventory
- [x] 2.4 Add a failing unit test that a workflow role holding zero or several skills raises, and that a missing or empty role raises
- [x] 2.5 Run the new tests and confirm each fails for the intended reason before implementing

## 3. Implement role discovery

- [x] 3.1 Add the `workflow` and `companion` role identifiers and a packaged-skill error type to `src/zpp/artifacts/__init__.py`
- [x] 3.2 Implement the role scan over `importlib.resources`, recognising a skill only by its `SKILL.md` and ordering by casefolded then exact name
- [x] 3.3 Reimplement `packaged_workflow_skill()` on the workflow role with the exactly-one constraint
- [x] 3.4 Replace the authoring-skill loader with a companion-role loader and delete `PACKAGED_AUTHORING_SKILL_NAMES`
- [x] 3.5 Update the module's public exports
- [x] 3.6 Run the section 2 tests to green

## 4. Bind the discovered inventory through the CLI

- [x] 4.1 Update `src/zpp/cli/initialization.py` to project every discovered companion skill in discovery order
- [x] 4.2 Update `src/zpp/cli/reset.py` so preflight and removal projections derive from discovery rather than a name list
- [x] 4.3 Verify `zpp workflow install|update|remove` still manages only the workflow skill and native hook
- [x] 4.4 Update `features/support/contracts.py` so reset projection order and initialization result counts derive from the discovered inventory

## 5. Vendor the zmem companion skills

- [x] 5.1 Vendor `zmem-author-commits` into the companion role as a byte-faithful copy of upstream
- [x] 5.2 Vendor `zmem-query-memory` into the companion role as a byte-faithful copy of upstream
- [x] 5.3 Confirm `zmem-design-extensions` is absent from the packaged inventory
- [x] 5.4 Add a unit test pinning the packaged companion inventory to the four expected skills
- [x] 5.5 Update per-agent asset count and order assertions in `tests/unit/test_cli.py` and `tests/integration/test_end_to_end.py`

## 6. Shape and verify observable behavior

- [x] 6.1 Add capability-owned Gherkin for discovering the companion inventory and for projecting one lifecycle result per discovered asset
- [x] 6.2 Add capability-owned Gherkin for reset targeting every discovered companion skill
- [x] 6.3 Run the relevant native Behave feature surface and confirm every shaped obligation is covered and passing

## 7. Automate vendored-skill synchronisation

- [x] 7.1 Add a GitHub Actions workflow triggered on `pyproject.toml` updates that replaces both vendored directories from `zmem` default-branch HEAD
- [x] 7.2 Make the workflow commit directly to the default branch only when content actually changed, producing no commit on an identical sync
- [x] 7.3 Confirm the workflow touches only the two vendored directories and never other packaged skills

## 8. Reconcile and finalize

- [x] 8.1 Update `README.md` where it names the packaged authoring pair or the reset inventory
- [x] 8.2 Run lint, format, the complete unit and integration test suites, and a clean package build
- [x] 8.3 Reconcile canonical specs from the mature green behavior and archive the change
