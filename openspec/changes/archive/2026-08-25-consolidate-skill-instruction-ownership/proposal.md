## Why

The packaged workflow skills repeat lifecycle and agent-operation instructions across
playbooks and components, making the guidance longer and allowing copies of the same
rule to drift. The instruction family needs one clear ownership hierarchy while
remaining complete enough for an agent to follow each selected workflow and stage.

## What Changes

- Reduce complete `zpp-*` playbooks to their ordered orchestration, custom branches,
  and workflow-specific judgment.
- Place repeatable stage behavior in the `zpps-*` stage or adapter that performs it.
- Place lifecycle guarding shared by multiple stages in `zpps-workflow-kernel`
  without making the kernel a dispatcher or moving capability-local procedures into
  it.
- Remove generic agent knowledge instead of relocating it into ZPP runtime or JSON
  contracts.
- Add focused conformance checks that prevent duplicated ownership from returning
  while preserving standalone stage admission and complete bounded procedures.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Define the ownership hierarchy and compactness
  constraints for complete playbooks, bounded components, and the guard-only kernel.

## Impact

- Packaged Markdown skills under `src/zpp/artifacts/skills/workflow/`.
- Consolidated workflow-skill conformance tests and canonical specification.
- No ZPP command, runtime schema, component JSON contract, or public API change.
