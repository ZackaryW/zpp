---
name: zpps-verify-repository
description: Run already selected repository verification targets read-only; do not discover product facts, repair failures, or judge OpenSpec change satisfaction.
---

# Verify repository evidence

## Admit repository verification

Admit this component only when an active playbook configures this exact verification
or the caller's immediate operation is to execute established repository checks for
an identified scope. Required readiness is a repository or capability target plus a
declared command source or an explicit need to resolve only command authority. Use
exploration for unresolved product, dependency, API, or integration evidence, and a
separate mutating component to repair any observed failure.

Require exact repository roots, changed-path or capability scope, shaped BDD
obligations, and either commands
resolved from repository configuration or an explicit owner choice. Ask for a choice
when command authority is ambiguous; never invent executable text. This operation is
read-only and does not require a kernel delegation.

Run scenario-selected capability BDD through the public system, focused unit tests for
pure case matrices, the relevant complete native test surface, supported-interpreter
and lock checks, lint, format, and a clean package build through the declared backend.
Run each relevant layer rather than substituting a narrow success for a broader gate.

Apply `bdd-execution` only as contextual mode advice. Run native capability BDD when
no `zpp.behave.yaml` exists. When the caller explicitly selected optional
coordination, use `--all` for complete mode, or `--gate zpps-workflow-kernel` only
when that exact gate is declared; otherwise use deterministic affected selection.
Manual mode returns `owner-choice-required`. Disabled mode may omit BDD only when
alternate relevant verification exists and no shaped obligation remains unsatisfied.

Return `completed`, `blocked`, or `owner-choice-required`, exact commands, targets,
exit statuses, material output, coverage of each required layer, and sufficiency gaps.
Failed or insufficient evidence remains failed. This read-only component never edits
planning or product artifacts or judges OpenSpec satisfaction.
