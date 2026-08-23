## Why

Automatic workflows currently turn legitimate capability and test edits into lease violations because ZPP forwards every changed path to Bundler's OpenSpec-only audit. The newest workflow decomposition also blurred the boundary between scenario-owning `zpp-*` playbooks and reusable `zpps-*` stages, allowing combined prose sections and inferred skips to replace distinct, audited utility-planning and utility-maturation actions.

## What Changes

- Make ZPP's runtime classify changed paths against registered repository roots, audit only OpenSpec paths through Bundler, accept repository-local non-OpenSpec paths as outside lease scope, and continue rejecting unknown roots or OpenSpec paths owned by unheld stores.
- Return explicit audited, ignored, and violating path evidence so automatic coordination remains inspectable without blocking capability-local BDD, application, or test files.
- Preserve `zpp-*` skills as scenario-specific workflows that execute reusable `zpps-*` stage skills, with `zpp-auto` transferring control to exactly one selected workflow in the same invocation.
- Restore each workflow stage as a distinct visible action with its own same-revision result; in particular, utility planning and utility maturation SHALL NOT be combined or skipped by a workflow-level inference.
- Make the workflow kernel audit the selected stage, complete predecessor outcomes, invalid evidence, owned effects, and observed result without selecting or dispatching a stage itself.
- Validate that every complete packaged workflow declares the full ordered stage-component sequence, rather than checking only a Ponytail-before-wire token pair.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-bundler-integration`: Clarify that ZPP automatically separates repository-local product paths from Bundler's OpenSpec authority audit and exposes both classifications.
- `consolidated-workflow-skill`: Re-establish scenario-owning workflows, reusable stage skills, same-invocation auto handoff, and distinct audited stage progression.

## Impact

- Runtime Bundler adapter and lease CLI result models.
- Packaged `zpp-auto`, complete playbooks, and `zpps-workflow-kernel` instructions.
- Packaged-workflow stage-sequence validation utilities and focused unit tests.
- Capability-owned Behave support, bindings, scenarios, and canonical OpenSpec traces for public audit behavior.
