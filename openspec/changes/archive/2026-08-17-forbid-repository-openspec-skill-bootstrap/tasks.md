## 1. Workflow Boundary

- [x] 1.1 Update the packaged `zpp-workflow` skill to consume only the exact ZPP-provisioned OpenSpec operation skills and prohibit workflow-owned initialization, generation, installation, projection, repair, or substitution.
- [x] 1.2 Define the blocking handoff for missing, invalid, or stale operation skills and preserve ordinary repo-local `openspec/` planning operations.

## 2. Specification Reconciliation

- [x] 2.1 Add the no-local-bootstrap requirement to the canonical `consolidated-workflow-skill` specification.
- [x] 2.2 Reconcile the canonical `openspec-skill-provisioning` requirement with `zpp init` creation, `zpp sync` repair, disposable generation, Agent Router projection, and user-scope exclusivity.
- [x] 2.3 Remove the obsolete canonical `Forced complete initialization` requirement and preserve `zpp sync --force` as the ownership-safe repair path.
- [x] 2.4 Inspect the workflow instructions, both deltas, both canonical specifications, current lifecycle implementation, and existing generation tests for a coherent authority boundary.

## 3. Verification And Finalization

- [x] 3.1 Record that this governed prose-only change creates no executable public behavior, Gherkin, BDD, utility-plan, unit-TDD, or product-wiring obligation.
- [x] 3.2 Run strict OpenSpec validation, diff checks, lock validation, supported-interpreter verification, lint, format, the complete test suite, and a clean build through the declared backend.
- [x] 3.3 Use `zmem-author-commits` for each material stage gate under the confirmed end-to-end authority and inspect every resulting SHA with `zmem show`.
- [x] 3.4 Archive the completed OpenSpec change and commit only remaining finalization-owned work without collapsing prior checkpoints.
