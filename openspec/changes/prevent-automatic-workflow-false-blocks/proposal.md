## Why

Automatic workflows currently turn legitimate capability and test edits into lease violations because ZPP forwards every changed path to Bundler's OpenSpec-only audit. The newest `zpp-auto` handoff also relies on unenforced prompt sequencing, so a selected playbook can reach wiring without an observed `zpps-planning-ponytail` result even though every playbook declares that stage.

## What Changes

- Make ZPP's runtime classify changed paths against registered repository roots, audit only OpenSpec paths through Bundler, accept repository-local non-OpenSpec paths as outside lease scope, and continue rejecting unknown roots or OpenSpec paths owned by unheld stores.
- Return explicit audited, ignored, and violating path evidence so automatic coordination remains inspectable without blocking capability-local BDD, application, or test files.
- Require `zpp-auto` to transfer control within the same workflow invocation and require every selected complete playbook to obtain an actual `zpps-planning-ponytail` result before wiring.
- Make the workflow kernel reject wiring progression when applicable utility-planning evidence is missing; only the Ponytail component may return `skipped: not applicable`.
- Add structural packaged-playbook validation and focused regression coverage for the required Ponytail-before-wire contract without restoring the obsolete monolithic stage dispatcher.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-bundler-integration`: Clarify that ZPP automatically separates repository-local product paths from Bundler's OpenSpec authority audit and exposes both classifications.
- `consolidated-workflow-skill`: Require same-invocation auto handoff and evidence-backed Ponytail completion or skip before wiring.

## Impact

- Runtime Bundler adapter and lease CLI result models.
- Packaged `zpp-auto`, complete playbooks, and `zpps-workflow-kernel` instructions.
- Packaged-workflow structural validation utilities and focused unit tests.
- Capability-owned Behave support, bindings, scenarios, and canonical OpenSpec traces for public audit behavior.
