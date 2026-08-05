## 1. Executable Scope Contract

- [x] 1.1 Rewrite workflow lifecycle feature examples so unqualified install, update, and removal target global scope and `--local` selects repository scope.
- [x] 1.2 Add executable rejection examples for a positional target without `--local`, removed `--global`, and local-only install options used in global scope.

## 2. CLI Scope Inversion

- [x] 2.1 Replace the workflow lifecycle `--global` parameters with `--local` and invert the shared CLI-to-core scope mapping.
- [x] 2.2 Validate target, `--force`, and `--with-openspec` combinations before lifecycle mutation while preserving current-directory local targeting.

## 3. Documentation and Verification

- [x] 3.1 Update README workflow examples and migration-facing help expectations for global-default and explicit-local syntax.
- [x] 3.2 Run focused workflow lifecycle tests, the complete unit and BDD suites, and strict OpenSpec validation.
