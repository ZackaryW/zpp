## Why

Agents can currently select a mutating `zpps-*` component from the caller's eventual product outcome even when the caller's immediate bounded operation is only to discover or validate unresolved evidence. That admission error grants the wrong procedure before its prerequisites are known and can cause an agent to continue under a mutating stage instead of reporting the mismatch.

## What Changes

- Define one normative admission rule across the complete `zpps-*` component family: classify the caller's immediate bounded operation, not the eventual desired outcome.
- Give `zpps-explore` precedence when the next necessary work is read-only discovery or validation of unresolved external or repository evidence.
- Require mutating components to be admitted only for an already-resolved exact operation with explicit mutation intent or exact playbook configuration.
- Default ambiguous read-versus-write admission to read-only exploration or one focused clarification.
- Require an agent that detects a component mismatch to report it immediately and stop using that component before continuing under a newly selected operation.
- Align every packaged `zpps-*` discovery description and the workflow's normative routing guidance with the same admission boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Define systematic component-admission precedence, mutation eligibility, ambiguity handling, and immediate misrouting reporting for the complete `zpps-*` family.

## Impact

- Packaged Markdown skills under `src/zpp/artifacts/skills/workflow/zpps-*/SKILL.md`, including their discovery metadata.
- Workflow playbooks and triage guidance where they select bounded components.
- Consolidated workflow acceptance coverage and focused skill-contract tests.
- No AppBuilder product behavior, OpenSpec CLI behavior, or compatibility identity is introduced.
