# Agent workflows

ZPP ships a complete workflow family for coding agents. The family combines outcome
entry playbooks, one lifecycle kernel, bounded stages, exact OpenSpec adapters, and a
repository verifier. Workflow invariants and authority live in those skills, not in
traits or reminder state.

## Install and update

`zpp init` installs the user-scope workflow family, companion skills, and native
trait hook together. The grouped workflow commands offer narrower project- or
user-scope lifecycle operations:

```powershell
zpp workflow install --agent codex --target .
zpp workflow update --agent codex --target .
zpp workflow remove --agent codex --target .

zpp workflow install --agent codex --global
```

Agent Router owns all workflow skill and native hook destination mutations. A
directory is a packaged skill only when it contains `SKILL.md`; a missing, invalid,
or unexpected workflow member fails family loading instead of producing a partial
installation.

## Packaged roles

Packaged skills live under `zpp/artifacts/skills/{role}/{skill}`.

- The `workflow` role is a fixed canonical inventory loaded in entry, kernel, stage,
  adapter, and repository-verifier order.
- The `companion` role is discovered by directory scan in deterministic name order.

Companion skills include repository authoring for traits and verification plus
vendored zmem commit-authoring and memory-query skills. They do not run from hooks or
workflow transitions and do not add CLI commands.

## Reminder runs

A complete playbook starts one target-scoped reminder before lifecycle work:

```powershell
zpp workflow run start zpp-generic-workflow `
  --root C:\path\to\repository `
  --change add-audio-player
```

The returned checklist is a mutable reminder snapshot, not execution authority.
Callers can inspect it, compare an explicitly selected component, record an accepted
matching result, customize stage entries, or stop it:

```text
zpp workflow run status --root ROOT --change CHANGE
zpp workflow run check --root ROOT --change CHANGE --component COMPONENT
zpp workflow run record --root ROOT --change CHANGE --component COMPONENT --result RESULT
zpp workflow run stage insert|delete|modify|upsert ...
zpp workflow run stop --root ROOT --change CHANGE
```

The reminder never grants mutation, checkpoint, archive, bypass, or continuation
authority. It records progress only after a component returns an accepted result.

## Lifecycle shape

The standard playbooks expose these concerns in order when applicable:

1. Clarify the product agreement using owner statements and current evidence.
2. Shape public behavior and BDD authority only for observable obligations.
3. Plan utility responsibilities with the Ponytail reuse ladder.
4. Mature planned utilities from relevant RED evidence to GREEN.
5. Wire proven utilities through the real public composition boundary.
6. Form specifications without duplicate BDD/OpenSpec scenario authority.
7. Verify the repository and the identified OpenSpec change.
8. Finalize from already supplied evidence and preserve the change separately.

Not every change needs every operation. A stage must return its own truthful
not-applicable result, or an owner must customize an inapplicable reminder stage;
the workflow must not fabricate BDD, planning, tests, or archive evidence.

## Consultation and feasibility

Clarification precedes planning. It establishes an evidence-backed agreement
skeleton, exposes outcome-changing choices with background and tradeoffs, and records
whether a prototype is needed. A needed proof of concept is bounded and disposable;
its evidence returns to clarification before planning continues. Routine artifact
corrections can skip a prototype when current files and command output directly prove
feasibility.

## Native integrations

The native context hook invokes trait resolution automatically:

- Codex and Claude Code use JSON SessionStart hooks.
- Kimi uses a TOML SessionStart hook.
- Pi uses a TypeScript `before_agent_start` extension.

There is no resolver skill, manual hook invocation command, or UserPromptSubmit trait
resolution hook. A separate prompt-stage reminder hook is installed only for agents
whose Agent Router integration exposes a context-bearing prompt event.

## Authority boundaries

The workflow kernel owns shared admission, lease coordination, changed-path audits,
checkpoints, archives, and lifecycle completion. Bounded components own only their
specific procedure and evidence.

Automatic continuation does not answer unresolved owner decisions. Git push, GitHub
merge actions, and cloud-environment operations always require separate explicit
authorization.

See [OpenSpec and Bundler coordination](coordination.md) for mutation leases and
[Repository verification](verification.md) for evidence selection.
