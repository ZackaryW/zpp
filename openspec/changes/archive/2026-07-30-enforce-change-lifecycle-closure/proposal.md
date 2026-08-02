## Why

ZPP can currently complete a green, specified workflow while leaving a consumed
OpenSpec change active without an owning stage. That silent stale state makes the
workflow's completion claim false and obscures which planning artifacts remain
authoritative.

## What Changes

- Treat every OpenSpec change selected, created, or consumed by a ZPP workflow as
  part of that workflow's related change set.
- Require every related change to have one explicit disposition before workflow
  completion:
  - archive the mature product change through the owning OpenSpec finalizer;
  - discard a disposable utility companion after its verified TDD pass;
  - discard a temporary internal anchor when its declared consumer condition has
    been satisfied; or
  - keep genuinely unfinished work active only under an identified owning stage.
- Snapshot/select active changes at workflow entry and audit the related change
  set again after finalization.
- Prevent the workflow from reporting completion while a consumed related change
  remains active without an owner.
- Leave unrelated active changes untouched; closure does not require the global
  OpenSpec change list to be empty.
- Keep lifecycle tracking as workflow/session state rather than adding it to the
  product proposal or authored trait files.
- Strengthen utility-companion disposal with a post-deletion absence check.
- Make the automatic-workflow trait state the concise completion invariant while
  retained skills own their stage-specific lifecycle operations.
- Discard the consumed `establish-workflow-skills` internal anchor once the new
  closure policy is mature.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `standard-workflow-traits`: Automatic workflow completion requires lifecycle
  reconciliation of every related OpenSpec change without touching unrelated
  active work.
- `workflow-skill-distribution`: Permanent workflow skills must assign and verify
  the terminal disposition owned by each change type before completion.

## Impact

- Updates the packaged `automatic-workflow` trait.
- Updates the permanent workflow skills that select, dispose, and finalize
  OpenSpec changes.
- Adds executable workflow-policy coverage to the existing Gherkin contract.
- Does not add a new workflow skill, CLI command, dependency, persistent lifecycle
  registry, or product serialization format.
