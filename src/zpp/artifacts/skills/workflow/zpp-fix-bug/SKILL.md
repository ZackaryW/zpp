---
name: zpp-fix-bug
description: Run the complete ordered ZPP playbook for an externally observable defect correction while preserving the regression and avoiding adjacent redesign.
---

# Correct a public defect

## Registered execution

Before lifecycle work, run:

`zpp workflow run start zpp-fix-bug --root <root> --change <change>`

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

### Clarify the failure

Use `zpps-clarify` to preserve the observed failure, affected consumer, expected public
behavior, reproduction conditions, and regression boundary. Do not broaden the defect
into redesign without an explicit owner correction. Use `zpps-explore` only for an
exact unresolved reproduction fact and re-enter.

### Plan the correction

Use an exact `planning-operation-required` signal when present. Otherwise update an
existing applicable change or use `zpps-propose-change` for a complete defect plan.
Use scaffold or one-artifact continuation only when explicitly selected. The accepted
plan must name the regression and exclude adjacent redesign.

### Configure correction stages

- Give `zpps-shape-bdd` the public failure and require the regression RED through the
  real system with feature-side authority only.
- Limit Ponytail planning and `zpps-mature-utilities` to the smallest responsibilities
  implicated by the failure; a contradiction returns to clarification or plan update.
- Give `zpps-wire` the regression, proven correction, and actual public composition
  owner, and require scenario-specific GREEN.
