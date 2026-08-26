---
name: zpp-scaffold
description: Run the complete ordered ZPP playbook for product-bearing repository or capability structure, with behavior stages applied only when observable behavior exists.
---

# Establish product-bearing structure

## Registered execution

Before lifecycle work, run:

`zpp workflow run start zpp-scaffold --root <root> --change <change>`

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

### Clarify the structure

Use `zpps-clarify` to distinguish product-bearing structure from artifact-only
maintenance, installation, or compatibility work. Identify the owning package or
application, public composition boundary, required files, and non-goals. Use
`zpps-explore` only for an exact unresolved repository fact and re-enter.

### Plan the scaffold

Use `zpps-new-change` for an explicit scaffold-and-stop request, `zpps-propose-change`
for a resolved end-to-end scaffold, or the exact update or one-artifact continuation
operation for an existing change. The plan must name the product-bearing owner and
exclude OpenSpec installation, generated skills, and compatibility aliases.

### Assess feasibility

After planning, route a `needed` prototype verdict through `zpps-explore` and re-enter
Clarify before the next registered stage.

### Configure structural stages

- Give `zpps-shape-bdd` only externally observable effects. Require its own
  evidence-backed skip for structure with no public behavior; never fabricate BDD for
  filesystem wording or prompt policy.
- Use Ponytail planning and maturation only for a reusable bootstrap utility.
- Use `zpps-wire` only for an accepted public composition point; structure-only work
  requires the component's own not-applicable result plus structural evidence.
