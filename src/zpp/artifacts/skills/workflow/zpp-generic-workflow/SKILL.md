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

## Custom configuration

### Clarify

Use `zpps-clarify` to decompose the mixed request only enough to form one accepted
change agreement. Preserve explicit relationships among capability, defect,
scaffold, and maintenance concerns; do not silently split the change or switch to a
specialized playbook after registration. Use `zpps-explore` only for an exact
`exploration-required` question and re-enter clarification.

### Plan the change

Use an exact `planning-operation-required` signal when present. Otherwise select
`zpps-propose-change` for a fully understood new change, `zpps-update-change` for
existing artifacts, `zpps-continue-change` for one requested next artifact, or
`zpps-new-change` for scaffold-and-stop. Use `zpps-ff-change` only when the owner
explicitly requested fast-forward planning for already complete intent.
