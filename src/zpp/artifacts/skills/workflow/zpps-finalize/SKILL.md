---
name: zpps-finalize
description: Assemble and assess already supplied phase, verification, and archive evidence read-only; do not create missing evidence or complete the lifecycle.
---

# Assemble final change evidence

## Admit finalization assessment

Admit this component only when an active playbook configures this exact assessment or
the caller's immediate operation is to evaluate assembled lifecycle evidence for a
known change bundle. Required readiness is an identified bundle or change set and
the evidence currently available for finalization. Discovery, repository execution,
semantic verification, archive mutation, and bundle completion remain separately
admitted operations even when this assessment later reports they are required.

Require the accepted contract revision, exact repository and store roots, every change member,
retained Bundler owner and bundle identity when mutation occurred, completed-phase
and checkpoint evidence, changed-path inventory, and any repository verification,
semantic verification, and archive results already obtained by the caller. This
assessment is read-only and does not require prior kernel delegation.

Check that changed paths match the accepted scope and bundle membership. Require
truthful repository command evidence for every relevant shaped obligation and build
gate and semantic verification covering tasks, requirements, design, bindings,
duplicate authority, and orphan authority. Classify terminal preservation before
requiring an archive result.

Use memory folding only when all durable information fits one or more precise zmem
entries and current normative authority is already complete without retaining the
change. A change is not foldable when it introduces or revises a requirement,
scenario, public contract, nested or branching logic, architecture or ownership
boundary, compatibility promise, security or safety constraint, migration, or any
decision whose full force depends on the planning artifacts. Simple wording,
metadata, or flat variable additions may qualify only when implementation and
verification are complete, no canonical specification effect remains, the proposed
zmem entries preserve the complete durable decision and rationale, and the owner has
explicitly selected memory folding for the exact change. Uncertainty selects normal
archive.

Return one of:

- `repository-evidence-required` with exact missing targets and sufficiency criteria;
- `change-verification-required` with the change identities and evidence to assess;
- `memory-fold-required` with the exact eligible change, non-foldability audit,
  proposed zmem content, and required explicit owner authority;
- `archive-required` with the exact single or bulk archive scope;
- `blocked` with failed or inconsistent evidence; or
- `completed` with the assembled paths, verification, and archive identities.

The caller explicitly invokes the signaled component and re-enters finalization with
its result. Accept `memory-folded` evidence only when it identifies the inspected
zmem-bearing commit, proves the active change was removed, proves no archive path was
created, and carries the exact owner authority. This assessment never converts
insufficient evidence into success, executes a signaled action, or completes a bundle.
