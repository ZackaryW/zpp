## Why

The general workflow currently exposes its internal cross-repository coordination provider without giving agents one bounded operation guide for the actual workspace lifecycle. Canonical OpenSpec scenarios also repeat executable behavior after that behavior has acquired an authoritative BDD feature, creating two scenario bodies that can drift.

## What Changes

- Add a packaged `zpp-workspace-management` companion skill that owns exact cross-repository topology, workspace, lock, successor, reconciliation, handoff, and cleanup command guidance while using the existing coordination commands internally.
- Remove provider-specific OpenLease wording from the general `zpp-workflow` skill and delegate cross-repository workspace operations to the new companion skill.
- Represent each BDD-covered OpenSpec scenario as an exact feature target instead of repeating its executable steps; retain complete OpenSpec scenario bodies when no qualifying BDD target exists.
- Require both workflow specification formation and OpenSpec maintenance to validate each feature target, its capability ownership, its scenario-selected executable binding, and its observed verification before moving or removing duplicated scenario content.
- Preserve strict OpenSpec structure by keeping a target-form `#### Scenario:` block for feature-owned behavior.

## Capabilities

### New Capabilities

- `workspace-management-skill`: Defines the packaged manual companion skill and its bounded use of existing cross-repository coordination commands.

### Modified Capabilities

- `consolidated-workflow-skill`: Delegates workspace operations without exposing the internal provider and forms canonical specs with BDD target scenarios instead of duplicated executable steps.
- `openspec-maintenance-skill`: Reconciles BDD-covered spec scenarios to verified feature targets while preserving every scenario that lacks qualifying BDD coverage.

## Impact

The change affects packaged workflow and companion skill artifacts, their UI metadata and references, and the three listed canonical capabilities. It adds no ZPP CLI command and changes no OpenLease, Agent Router, or ZPP implementation logic; the discovered companion inventory and resulting projected integration gain the new skill through the existing artifact-loading behavior.
