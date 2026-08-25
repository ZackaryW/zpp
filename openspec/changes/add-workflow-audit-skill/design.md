## Context

Complete workflow ordering now lives in packaged JSON contracts, while custom decisions and branches remain in Markdown playbooks. Component metadata lives in component JSON, substantive procedures remain in component skills, runtime reminders are implemented by the workflow CLI and kernel, and acceptance authority is split across canonical OpenSpec, Behave, and Python tests. A useful audit must compare these layers without becoming another sequencing authority or mutating real coordination state.

## Goals / Non-Goals

**Goals:**

- Give maintainers one explicit local audit entry point.
- Drive a synthetic OpenSpec change through every complete packaged workflow.
- Make omissions, contradictions, and untested branches visible with reproducible evidence.
- Support owner-guided gap closeout and fresh targeted reruns.

**Non-Goals:**

- Add a workflow stage, runtime gate, daemon, or revision history.
- Infer authority to repair skills, contracts, runtime code, specifications, tests, reminders, or leases without an accepted interactive closeout decision.
- Prove arbitrary component business behavior beyond the workflow coordination surface.
- Replace strict contract loading, Behave, pytest, or semantic change verification.

## Decisions

### Package the audit as a companion skill

`zpp-audit-workflows` will live in the packaged companion role. It is an explicit maintainer operation that observes complete workflows; it is neither a complete product playbook nor a reusable lifecycle component. This keeps it out of workflow contract registration and prevents the audit from auditing itself as a workflow.

Alternative: add it as a `zpp-*` playbook or `zpps-*` stage. Rejected because either choice would grant it a misleading lifecycle identity and introduce circular sequencing concerns.

### Discover assignments from packaged workflow JSON

The coordinator will enumerate `src/zpp/artifacts/workflow_contracts/workflows/*.json`, parse structure with `jq`, and cross-check the repository's packaged loader/tests. For every contract, it will resolve the matching playbook and referenced component contracts and skills. The skill will not duplicate the four current workflow names.

Alternative: list workflows in the skill for simpler prompts. Rejected because the audit list would drift from the artifact inventory it is meant to inspect.

### Use a distinct subagent and empty Git/OpenSpec workspace per workflow

The coordinator will create one bounded assignment per workflow. Each assignment uses a unique temporary directory, runs `git init`, runs `openspec init <root> --tools none --no-animation`, creates a synthetic OpenSpec change, and selects a unique global `zpp --path <temporary-home>` product home. It never registers the disposable root as a persistent OpenSpec store. Limited delegation slots cause queuing, not assignment or workspace reuse.

The subagent receives only its workflow identity, source root, evidence checklist, isolation requirement, and report schema. It may mutate its disposable repository to satisfy mock prerequisites, but it must preserve each initial failure and remain read-only in the ZPP source checkout until an interactive source correction is accepted. The coordinator records live `git status`, workflow reminder status, and lease status before and after simulations to detect contamination.

Alternative: one subagent audits all workflows. Rejected because cross-workflow assumptions and shared simulation state would hide precisely the continuity and specialization failures under audit.

### Drive the playbook sequence, not only reminder operations

For its synthetic request, the subagent follows the assigned playbook as an agent would. It starts registration, examines the first pending stage, reads that stage's component contract and skill, builds a bounded mock input and result, evaluates every playbook-owned branch, checks and records the result through the real reminder CLI, and advances only after the observed result is accepted. The synthetic repository carries minimal real OpenSpec planning artifacts and is validated and archived locally during closeout.

The simulation uses real Git, OpenSpec, workflow reminder, JSON parsing, and verification commands. It mocks product-specific component work so the audit evaluates orchestration rather than inventing a full product. A mock result must still satisfy the component's declared vocabulary and stopping boundary. Planning, sync, verification re-entry, finalization, and archive branches cannot be skipped merely because they are not reminder stages.

Alternative: exercise only `start`, checklist CRUD, `check`, and `record`. Rejected because those commands can pass while the playbook's custom branches are incomplete or contradictory.

### Keep semantic comparison agent-driven and mechanically evidenced

The audit skill will keep coordination and safety instructions in `SKILL.md` and put the detailed evidence matrix and result schema in `references/audit-contract.md`. Subagents may inspect source and run established focused tests, but every conclusion must cite an exact path, symbol, scenario, test, or captured command result. The skill will classify drift by authority layer rather than reduce results to wording matches.

Alternative: add a deterministic source-text linter. Rejected because playbook branches and implementation semantics require judgment, while wording checks would create brittle false confidence.

### Maintain a gap ledger through interactive closeout

Each subagent records fixture gaps and source gaps separately. It may close a fixture gap inside its temporary repository and continue, while retaining the original failure and repair evidence. Source gaps return to the coordinator with the exact authority layer, transition, expected/observed behavior, and proposed closeout.

The coordinator presents source gaps interactively. Each becomes `accepted-fix`, `deferred`, `rejected`, or `blocked`; no gap disappears merely because the sequence continued under a mock assumption. An accepted fix is applied only within the current repository change's authority and updates design, implementation, and exact verification together. The affected workflow then receives a fresh subagent, Git repository, OpenSpec root, product home, and audit revision. Completion requires a closed mock sequence for every workflow and an explicit closeout state for every gap.

## Risks / Trade-offs

- **Agent judgment can vary** → Require a fixed evidence matrix, typed finding categories, reproducible commands, and explicit unexecuted checks.
- **Subagent availability may be lower than workflow count** → Queue assignments while preserving one distinct agent invocation per workflow.
- **Simulations could contaminate live state** → Use a unique temporary Git/OpenSpec repository and product home, avoid persistent store registration, capture pre/post Git/reminder/lease snapshots, and treat any difference as a failed audit invariant.
- **Mock results could conceal unusable component instructions** → Require each mock input/result to satisfy the actual component contract and skill boundary, record every assumption, and exercise every playbook-owned branch.
- **Closing gaps could expand mutation authority** → Keep source read-only until the maintainer accepts a specific closeout and apply it only inside the current repository change or a separately authorized repair.
- **The audit can become expensive** → Prefer targeted Behave scenarios and focused pytest selectors; reserve full-suite execution for a separately requested audit depth.
- **A source checkout may be incomplete** → Report missing layers as blocking evidence gaps instead of downgrading the audit silently.

## Migration Plan

1. Add the companion skill, reference contract, and UI metadata.
2. Add capability BDD and focused tests for disposable Git/OpenSpec initialization, per-workflow full-sequence closeout, isolation, gap classification, and interactive reruns.
3. Verify lifecycle projection includes the new companion through existing Agent Router composition.
4. Run an independent forward audit with one fresh subagent and disposable Git/OpenSpec workspace per complete workflow, close accepted gaps, and rerun affected workflows from scratch.

Rollback removes the companion skill and its capability-specific evidence without changing runtime workflow contracts or stored reminder formats.
