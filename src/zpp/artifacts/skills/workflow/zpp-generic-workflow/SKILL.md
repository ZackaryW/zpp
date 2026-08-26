---
name: zpp-generic-workflow
description: Run the complete current ZPP playbook for mixed, maintenance-oriented, or otherwise unspecialized product outcomes.
---

# Run the generic current workflow

## Registered execution

Before lifecycle work, run:

`zpp workflow run start zpp-generic-workflow --root <root> --change <change>`

Follow the returned checklist, including owner edits, as the current stage order.
Invoke its first pending component with only the custom configuration below and use
`zpps-workflow-kernel` for shared admission, authority, result, audit, and checkpoint
mechanics. This playbook selects visible component-result branches; neither reminder
state, the kernel, nor a component dispatches continuation or supplies missing owner
authority.

## Automatic continuation authority

Interpret explicit owner authority for this workflow invocation at three distinct
levels. `Proceed automatically` grants end-to-end continuation and covers ordinary
in-scope component confirmations after their exact proposed effects are shown, but
every unresolved Clarify decision remains an owner gate. When that progression grant
also includes an unambiguous request to make best decisions, resolve the current or
next Clarify gate and consume that decision authority when the gate completes. An
unambiguous full-authority statement retains both decision and continuation authority
across later Clarify re-entry until the owner revokes it prospectively.

Re-enter Clarify whenever new evidence or a contradiction changes the accepted
contract and invalidate downstream results from the superseded revision. A consumed
one-gate delegation does not revive on re-entry; unrevoked full authority remains
applicable. Never infer any level from this skill's invocation, workflow reminder
state, or `zpp-auto` routing. No level authorizes Git push, a GitHub merge action, or
access to or mutation of a cloud environment; obtain separate step-by-step owner
authorization for each such operation.

## Custom configuration

### Clarify

Use `zpps-clarify` to decompose the mixed request only enough to form one accepted
change agreement. Preserve explicit relationships among capability, defect,
scaffold, and maintenance concerns; do not silently split the change or switch to a
specialized playbook after registration. Use `zpps-explore` only for an exact
`exploration-required` question and re-enter clarification.

### Plan the change

For a bounded correction to instruction artifacts with an owner-supplied file
boundary and no runtime behavior, use the owning artifact guidance and do not force
an OpenSpec planning operation merely because the artifact is packaged. Otherwise
use an exact `planning-operation-required` signal when present, or select
`zpps-propose-change` for a fully understood new change, `zpps-update-change` for
existing artifacts, `zpps-continue-change` for one requested next artifact, or
`zpps-new-change` for scaffold-and-stop. Use `zpps-ff-change` only when the owner
explicitly requested fast-forward planning for already complete intent.

### Assess feasibility

After any required planning, route a `needed` prototype verdict through
`zpps-explore` and re-enter Clarify before the next registered stage.

### Apply stage relevance

For the accepted instruction-artifact route, record truthful no-op results for
inapplicable registered stages. When an OpenSpec-only tail component has no such
result and no change or bundle exists, use the reminder's owner-edit interface to
remove that stage rather than fabricate evidence.
