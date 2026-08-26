---
name: zpp-new-feature
description: Run the complete ordered ZPP playbook for a new externally observable capability, using explicit bounded components and visible branches.
---

# Deliver a new public capability

## Registered execution

Before lifecycle work, run:

`zpp workflow run start zpp-new-feature --root <root> --change <change>`

Follow the returned checklist, including owner edits, as the current stage order.
Invoke its first pending component with only the custom configuration below and use
`zpps-workflow-kernel` for shared admission, authority, result, audit, and checkpoint
mechanics. This playbook selects visible component-result branches; neither reminder
state, the kernel, nor a component dispatches continuation or supplies missing owner
authority.

## Custom configuration

### Clarify the capability

Use `zpps-clarify` to frame one public capability, its consumers, observable behavior,
compatibility boundary, and acceptance conditions without choosing an implementation.
Use `zpps-explore` only for an exact `exploration-required` question and re-enter.

### Plan the capability

Preserve an explicitly selected change. For an existing plan, select the exact
`zpps-update-change` or one-artifact `zpps-continue-change` operation. For a resolved
new capability, use `zpps-propose-change`; use `zpps-new-change` only for an explicit
scaffold-and-stop request.

### Configure behavior stages

- Give `zpps-shape-bdd` the accepted public examples and capability owner; every
  executable example must end with feature-side authority and no corresponding
  OpenSpec scenario.
- Limit Ponytail planning and maturation to responsibilities required by the new
  capability, preserving distinct plan and maturation results.
- Give `zpps-wire` the real public composition owner and accepted feature bindings.
