## Context

See `proposal.md` for motivation. ZPP already has the required focused pieces: complete initialized-state validation, additive packaged-default planning, exact workflow ownership inspection, historical native-hook reconciliation, isolated OpenSpec generation with recorded version state, and rollback-capable filesystem mutation merging. They are currently composed only by separate initialization and workflow lifecycle paths.

The new command must discover existing global ownership without treating executable availability or directory names alone as installation authority. It must also avoid calling the executable upgrader from inside the running process.

## Goals / Non-Goals

**Goals:**

- Compose existing global ownership inspectors and planners behind one option-free command.
- Produce one complete preflighted mutation plan spanning the default profile and every discovered owned agent surface.
- Keep discovery deterministic across the fixed supported agent inventory.
- Reuse existing version and content ownership contracts instead of adding another update manifest.

**Non-Goals:**

- Upgrade the ZPP executable or OpenSpec executable.
- Install a missing ZPP workflow bundle.
- Add scope or agent-selection options to the top-level command.
- Inspect or mutate repository-local projections, authored project layers, caches, plugins, or trust state.

## Decisions

### Fixed global discovery, not selection

The command inspects Pi, Codex, and Claude Code in stable order. For each agent it classifies the global ZPP workflow projection and native integration using existing ownership evidence. A compatible or outdated managed workflow is included; an absent workflow is skipped unless a recognizable existing ZPP hook needs reconciliation; an unmanaged or malformed claimed workflow conflicts before mutation.

This makes `zpp update` a zero-configuration maintenance command. Reusing `--agent` was rejected because it would preserve the exact multi-command bookkeeping the new surface is meant to remove.

### Managed workflow implies complete integration maintenance

When a managed global ZPP workflow bundle exists, update composes the current bundle, current hook, and generated OpenSpec projection as one agent outcome. An absent associated OpenSpec projection is repaired because it is required by the already-installed complete workflow; an absent ZPP workflow bundle is never inferred from OpenSpec skills or hooks and remains absent.

The detected OpenSpec version is evaluated once. A verified generated projection with the same recorded value, including `null`, is preserved. A missing or changed projection is generated in the existing isolated temporary-project boundary before filesystem mutation. A ZPP-maintained plugin or framework matrix was rejected because OpenSpec owns its generated content.

### Hook-only maintenance requires recognizable ownership

An exact current or supported historical ZPP hook can be refreshed without a workflow bundle. A completely absent hook is skipped for an agent without a workflow, and unrelated native configuration is never enough to opt the agent into update. This preserves users who chose hook-only initialization without turning update into workflow installation.

### One transaction after external generation

Update first requires complete initialized user state, validates and plans the additive default merge, discovers every agent state, and performs any required OpenSpec generation. Only after all reads, generation, validation, and conflict checks succeed are the focused mutation plans merged and applied through the existing rollback-capable filesystem boundary.

The default profile remains authored state: existing files and values win, while missing packaged entries are added. Skill and generated projections remain manifest-owned state: intact historical projections may be replaced, but modified or unmanaged content rejects the operation.

### Separate bootstrap and maintenance help

The root Typer app registers an option-free `update` command. `init` help describes missing-state bootstrap and explicitly selected global hook configuration. `update` help describes refresh of initialized global state and installed integrations and explicitly excludes executable self-update. The README shows executable upgrade as the preceding external step.

## Risks / Trade-offs

- **[One conflict blocks otherwise independent agents]** → This is intentional atomicity; diagnostics identify the exact conflicting destination so the owner can resolve it before retrying.
- **[OpenSpec generation adds latency only for changed or missing projections]** → Detect the version once and preserve verified matching projections without regeneration.
- **[Hook ownership differs among agents]** → Reuse the existing exact current/historical hook contracts and add discovery tests for absent, recognizable, and conflicting states rather than heuristic text matching.
- **[Shared Pi or Claude skill roots contain multiple manifests]** → Keep ZPP workflow and OpenSpec ownership manifests independent and merge only non-overlapping owned paths.

## Migration Plan

1. Add public scenarios for help, absent/incomplete initialization, profile-only update, hook-only update, discovered complete workflows, conflicts, idempotence, and local isolation.
2. Add focused discovery/planning utilities and compose them through one global update core operation.
3. Register the Typer command, revise initialization help, and update the README upgrade sequence.
4. Verify focused utilities, bootstrap/workflow feature roots, the complete mapped audit, and strict OpenSpec reconciliation.

Rollback removes the top-level command and restores the previous help/README sequence. Existing state written by successful update remains compatible with the independent `workflow update` and hook initialization paths.
