---
name: zpp-audit-workflows
description: Audit this repository's complete ZPP workflows serially with one isolated subagent at a time, stopping after each result to close feedback before advancing.
---

# Audit workflows serially

This is a repository-maintainer skill. It is not a packaged ZPP artifact and does not
create an OpenSpec change or canonical specification for the audit mechanism itself.

Read [references/audit-contract.md](references/audit-contract.md) completely before
bootstrapping the mock base or assigning a workflow.

## Prepare once

1. Discover complete workflows from
   `src/zpp/artifacts/workflow_contracts/workflows/*.json`; do not maintain another
   workflow list.
2. Capture source Git status, the active workflow reminder, and retained lease state.
3. Create one temporary base folder with
   `scripts/mock_project.py bootstrap --base <path>`. The helper initializes Git and
   OpenSpec once, verifies both roots, and commits a neutral clean base.

## Run one workflow at a time

For the next workflow only:

1. Clone the immutable base with `scripts/mock_project.py clone`, selecting a fresh
   repository and product home.
2. Spawn exactly one subagent for that workflow and wait for its complete result. Do
   not pre-spawn, queue, or run another workflow concurrently.
3. The subagent starts the reminder with a unique synthetic change name, then follows
   the assigned playbook. The appropriate planning branch creates the synthetic
   change inside the clone; the neutral base contains no workflow-specific change.
4. Recapture source Git, reminder, and lease status as soon as the subagent returns.
   Treat an attributable difference as an isolation failure.
5. Review the workflow's result and recommendations before selecting another
   workflow.

When a recommendation is accepted, stop inventory progression. Re-enter the full
applicable ZPP phases in the source repository—planning, behavior shaping, utility
planning, utility maturation, wiring, specification formation/synchronization, and
verification—with independently visible skips for inapplicable phases. Then rerun
the same workflow in a fresh clone with a fresh subagent. Advance only when that
workflow closes or every recommendation is explicitly deferred, rejected, or
blocked.

Keep the ZPP source checkout read-only during a simulation. A subagent may repair
only its disposable clone and must preserve the before/after evidence. Never infer
source mutation, commit, archive, abandonment, bypass, or workflow-continuation
authority from this audit skill.
