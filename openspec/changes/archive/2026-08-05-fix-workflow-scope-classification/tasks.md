## 1. Source-level workflow contracts

- [x] 1.1 Extend the existing workflow-distribution Gherkin contract for pre-bootstrap request classification and justified monorepo feature ownership.
- [x] 1.2 Update `zpp-clarify-change` and `zpp-shape-feature`, including their packaged copies, to enforce the accepted boundaries.

## 2. Environmental release tooling

- [x] 2.1 Add fail-first native tests for valid, idempotent, invalid, and rollback behavior of the standalone version-bump script.
- [x] 2.2 Implement dependency-free `scripts/bump_version.py` with PEP 723 metadata, exact declaration preflight, lock regeneration, and failure restoration.
- [x] 2.3 Run the script for `0.9.6`, update only the existing product-identity expectation, and document the maintainer command.

## 3. Verification and distribution

- [x] 3.1 Run focused native tests, installed-skill BDD coverage, mapped behavior verification, the full test suite, strict OpenSpec validation, and an idempotent real script invocation.
- [x] 3.2 Reconcile canonical specs, archive the completed change, reinstall the global workflow bundle, and verify the installed skill content.
