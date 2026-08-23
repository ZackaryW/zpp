---
name: zpp-auto
description: Triage a product request through a complete non-mutating procedure and hand off exactly once to the matching current ZPP playbook.
---

# Triage one ZPP workflow

This playbook owns only classification and handoff. It never performs governed
mutation, acquires a lease, or inherits the selected playbook's sequence.

## 1. Frame the request

Preserve the user's words, explicit repository roots, accepted constraints, and
authority. Classify the requested outcome, not the likely implementation:

- new externally observable capability -> `zpp-new-feature`;
- correction of an externally observable defect -> `zpp-fix-bug`;
- product-bearing repository or capability structure -> `zpp-scaffold`;
- mixed, unsupported, maintenance-only, or unresolved outcome ->
  `zpp-legacy-workflow` at clarification.

Do not infer a store, change, mutation authority, checkpoint authority, or later
stage from repository files or prior artifacts.

## 2. Use `zpps-explore` only when classification needs evidence

Condition: the outcome cannot be classified without bounded read-only repository
evidence, but no owner decision is required.

Configure `zpps-explore` with the exact roots and classification question. Consume
only its observations, then repeat step 1. If evidence still leaves more than one
outcome, select `zpp-legacy-workflow`; do not keep exploring indefinitely.

## 3. Invoke one playbook and transfer control

Invoke the selected `zpp-*` playbook exactly once. This is an execution handoff,
not a recommendation or route report. Pass that invocation the original request,
exact roots, accepted classification evidence, accepted owner input,
owner-authorized end-to-end mode when explicitly granted, and only authority the
owner supplied. For the legacy fallback, invoke its first declared clarification
action. End-to-end mode permits that playbook to follow its declared branches; it
never answers owner decisions or supplies missing durable-owner, mutation,
checkpoint, or archive authority. Do not preselect any later action.

After invocation, transfer control to that playbook and do not return to triage.
The selected playbook owns its next action and all subsequent declared branches.
Never merely report the selected playbook and stop, invoke the kernel directly,
mutate artifacts during triage, add authority, or claim completion on the selected
playbook's behalf.
