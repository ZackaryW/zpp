## Context

The packaged family currently combines four kinds of prose in many files: complete
playbook orchestration, bounded component procedure, shared lifecycle guarding, and
generic reminders an agent already understands. Several identical or near-identical
blocks therefore appear in every complete playbook or across many components. The
JSON workflow contracts already own mechanical stage registration and component
contracts already own typed metadata, but this change does not expand either runtime
surface.

## Goals / Non-Goals

**Goals:**

- Give each ZPP-specific instruction one lowest valid owner.
- Make complete playbooks primarily readable as orchestration and custom branches.
- Keep each bounded component independently actionable while referring shared guard
  mechanics to the kernel.
- Remove generic agent reminders and materially reduce repeated prose.
- Preserve all workflow stages, authority boundaries, stopping boundaries, and
  failure behavior.

**Non-Goals:**

- Changing workflow order, CLI behavior, JSON schemas, leases, or runtime dispatch.
- Turning the kernel into a workflow selector or stage dispatcher.
- Moving capability-local procedure, declarations, bindings, or result semantics out
  of the component that owns them.
- Optimizing to a fixed line count at the expense of operational completeness.

## Decisions

### Use a four-way ownership test

Every candidate paragraph is classified before editing:

1. Workflow-only: sequence, custom configuration, or a workflow-specific branch;
   retain it in the complete playbook.
2. Component-owned: procedure or policy for one bounded stage/adapter; retain one
   complete form in that component and remove playbook copies.
3. Kernel-owned: pre-action admission, shared authority handling, lease coordination,
   result audit, checkpoint, or lifecycle completion shared by components; retain one
   complete form in the kernel and use concise references from components.
4. Agent-known: general advice with no ZPP-specific operational meaning; delete it.

This semantic test is preferred over mechanical deduplication because similar words
can implement different component-local failure or stopping rules.

### Keep concise integration seams

Playbooks continue to name each selected component or custom branch but do not repeat
that component's readiness, procedure, or result contract. Mutating components retain
the fact that a current kernel guard is required and the exact facts they supply, but
do not reproduce lease algorithms, checkpoint procedure, or workflow-continuation
prohibitions already owned by the kernel. This keeps direct invocation understandable
without reintroducing full lifecycle copies.

### Verify structure and semantics, not prose snapshots

Focused tests will validate the required ownership boundaries, absence of selected
known duplicated blocks, valid packaged skills, and unchanged workflow/component
contract coverage. Tests may measure duplicate structure as maintenance evidence but
will not turn literal skill wording into BDD acceptance authority. The BDD stage is
not applicable because this change introduces no new executable public-system
behavior.

## Risks / Trade-offs

- **A component becomes too terse for standalone use** → Retain its unique readiness,
  inputs, procedure, result, and failure behavior; remove only shared lifecycle detail.
- **Kernel becomes a hidden dispatcher** → Preserve its exact-action input contract
  and its prohibition on selecting or invoking continuation.
- **Mechanical shortening drops a distinct rule** → Build an ownership inventory and
  compare before/after semantic obligations before accepting edits.
- **Future edits reintroduce copies** → Add focused structural conformance tests for
  the ownership boundary rather than exact full-document snapshots.

## Migration Plan

Refactor the packaged source skills in one coherent pass, run focused skill and
workflow conformance checks, then synchronize the modified canonical requirement.
Installed copies are updated through the repository's normal packaging/sync lifecycle;
no runtime data migration is needed.
