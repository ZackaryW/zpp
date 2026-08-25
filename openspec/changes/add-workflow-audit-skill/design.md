## Context

Complete workflow ordering now lives in packaged JSON contracts, while custom decisions and branches remain in Markdown playbooks. Component metadata lives in component JSON, substantive procedures remain in component skills, runtime reminders are implemented by the workflow CLI and kernel, and acceptance authority is split across canonical OpenSpec, Behave, and Python tests. A useful audit must compare these layers without becoming another sequencing authority or mutating real coordination state.

## Goals / Non-Goals

**Goals:**

- Give maintainers one explicit local audit entry point.
- Independently simulate every complete packaged workflow.
- Make omissions, contradictions, and untested branches visible with reproducible evidence.
- Support owner-guided review and targeted reruns.

**Non-Goals:**

- Add a workflow stage, runtime gate, daemon, or revision history.
- Repair skills, contracts, runtime code, specifications, tests, reminders, or leases.
- Prove arbitrary component business behavior beyond the workflow coordination surface.
- Replace strict contract loading, Behave, pytest, or semantic change verification.

## Decisions

### Package the audit as a companion skill

`zpp-audit-workflows` will live in the packaged companion role. It is an explicit maintainer operation that observes complete workflows; it is neither a complete product playbook nor a reusable lifecycle component. This keeps it out of workflow contract registration and prevents the audit from auditing itself as a workflow.

Alternative: add it as a `zpp-*` playbook or `zpps-*` stage. Rejected because either choice would grant it a misleading lifecycle identity and introduce circular sequencing concerns.

### Discover assignments from packaged workflow JSON

The coordinator will enumerate `src/zpp/artifacts/workflow_contracts/workflows/*.json`, parse structure with `jq`, and cross-check the repository's packaged loader/tests. For every contract, it will resolve the matching playbook and referenced component contracts and skills. The skill will not duplicate the four current workflow names.

Alternative: list workflows in the skill for simpler prompts. Rejected because the audit list would drift from the artifact inventory it is meant to inspect.

### Use a distinct subagent and isolated product home per workflow

The coordinator will create one bounded assignment per workflow. Each assignment uses a unique temporary directory with the global `zpp --path <temporary-home>` option and a synthetic change identity. It exercises reminder start/resume, matching and mismatching checks, accepted recording, and insert/modify/upsert/delete behavior. Limited delegation slots cause queuing, not assignment reuse.

The subagent receives only its workflow identity, source root, evidence checklist, isolation requirement, and report schema. It must remain read-only outside temporary state. The coordinator records live `git status`, workflow reminder status, and lease status before and after simulations to detect contamination.

Alternative: one subagent audits all workflows. Rejected because cross-workflow assumptions and shared simulation state would hide precisely the continuity and specialization failures under audit.

### Keep semantic comparison agent-driven and mechanically evidenced

The audit skill will keep coordination and safety instructions in `SKILL.md` and put the detailed evidence matrix and result schema in `references/audit-contract.md`. Subagents may inspect source and run established focused tests, but every conclusion must cite an exact path, symbol, scenario, test, or captured command result. The skill will classify drift by authority layer rather than reduce results to wording matches.

Alternative: add a deterministic source-text linter. Rejected because playbook branches and implementation semantics require judgment, while wording checks would create brittle false confidence.

### Make interaction review-oriented

After all initial assignments return, the coordinator presents the aggregate result and one concise result per workflow. Owner corrections or requests for deeper inspection cause a fresh subagent assignment only for the selected workflow; existing results remain visible and are marked superseded only by the new evidence. No repair follows unless separately requested.

## Risks / Trade-offs

- **Agent judgment can vary** → Require a fixed evidence matrix, typed finding categories, reproducible commands, and explicit unexecuted checks.
- **Subagent availability may be lower than workflow count** → Queue assignments while preserving one distinct agent invocation per workflow.
- **Simulations could contaminate live state** → Use a unique temporary product home, synthetic change names, pre/post Git/reminder/lease snapshots, and treat any difference as a failed audit invariant.
- **The audit can become expensive** → Prefer targeted Behave scenarios and focused pytest selectors; reserve full-suite execution for a separately requested audit depth.
- **A source checkout may be incomplete** → Report missing layers as blocking evidence gaps instead of downgrading the audit silently.

## Migration Plan

1. Add the companion skill, reference contract, and UI metadata.
2. Add capability BDD and focused tests for packaged discovery, per-workflow assignment rules, isolation, evidence classification, and interactive reruns.
3. Verify lifecycle projection includes the new companion through existing Agent Router composition.
4. Run an independent forward audit with one fresh subagent per complete workflow.

Rollback removes the companion skill and its capability-specific evidence without changing runtime workflow contracts or stored reminder formats.
