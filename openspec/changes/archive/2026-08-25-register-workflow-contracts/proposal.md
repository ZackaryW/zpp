## Why

ZPP currently relies on repeated Markdown instructions and conversational continuity
to remember which workflow stage should run next. A lightweight persisted workflow
registration can keep the declared sequence visible across turns without turning the
kernel into a dispatcher or blocking flexible direct component use.

## What Changes

- Add strict packaged JSON artifacts that declare each complete `zpp-*` workflow's
  ordered reminder stages and each `zpps-*` component's mechanical metadata.
- Add `zpp workflow run` commands to start, inspect, stop, and directly customize a
  persisted reminder checklist for exact repository/change targets.
- Add a separate read-only `zpp-workflow-reminder` native hook for agents whose
  Agent Router adapter confirms a prompt-submission context event. The hook emits
  compact active-workflow status and remains silent when no workflow is active.
- Make workflow start idempotently resume an existing matching checklist and require
  complete packaged playbooks to start their registration before lifecycle work.
- Have the workflow kernel compare a requested component with the first pending
  registered stage, update matching stage outcomes, and return prominent structured
  warnings for out-of-sequence work while leaving execution allowed in reminder mode.
- Keep direct standalone `zpps-*` use available when no registered workflow governs
  the target, and keep read-only components usable without advancing the checklist.
- Reduce repeated mechanical sequencing, admission, and result wording in packaged
  skills while retaining workflow-specific branches and substantive component
  procedures in Markdown.
- Preserve Bundler as resource coordination: workflow reminder state may reference a
  bundle but is not embedded in, or made authoritative by, the lease model.

## Capabilities

### New Capabilities

- `workflow-registration`: Defines packaged JSON workflow/component contracts,
  reminder checklist lifecycle commands, persisted target-scoped state, direct user
  customization, and structured sequence comparison.

### Modified Capabilities

- `consolidated-workflow-skill`: Moves mechanical workflow declarations and common
  component metadata from repeated Markdown into validated JSON contracts while
  retaining custom playbook decisions and substantive component behavior in skills.

## Impact

- Affects packaged artifact discovery and validation under `src/zpp/artifacts/`.
- Extends the existing `zpp workflow` CLI with a nested runtime command group while
  preserving workflow skill installation, update, and removal commands.
- Extends the shared Agent Router-owned lifecycle inventory conditionally with the
  `zpp-workflow-reminder` hook without changing the existing `zpp-traits` hook.
- Adds product-home persistence and kernel-facing workflow reminder operations.
- Updates workflow skill packaging, source Markdown, unit tests, CLI integration
  tests, and behavior coverage for registration, resumption, customization, and
  out-of-sequence warnings.
- Does not add a strict workflow gate, automatic stage dispatcher, session binding,
  hook-owned state transition, or workflow-definition state to Bundler leases.
