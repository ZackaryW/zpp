---
name: zpp-auto
description: Triage one request non-mutatingly into a current ZPP playbook, an accepted direct artifact route, or a truthful no-handoff result.
---

# Triage one ZPP workflow

This playbook owns only classification and handoff. It never performs governed
mutation, acquires a lease, or inherits a selected playbook's sequence.

## Component admission invariant

Outcome routing and subordinate component admission are separate decisions. Use the
eventual product outcome only to select one `zpp-*` playbook; never use it to select
a `zpps-*` component. Before any `zpps-*` use, choose the exact configured component
from the immediate necessary operation and its evidence readiness, not change status,
task position, or imperative wording. Unresolved evidence admits `zpps-explore`;
unresolved outcome-changing owner policy admits `zpps-clarify`. Every configured
component remains subject to its own readiness and authority contract. Consume
`component-mismatch` as failed admission, report it immediately, and select no
continuation from inside the rejected component.

## 1. Frame the request

Preserve the user's words, explicit repository roots, accepted constraints, and
authority. Classify the requested outcome, not the likely implementation:

- new externally observable capability -> `zpp-new-feature`;
- correction of an externally observable defect -> `zpp-fix-bug`;
- product-bearing repository or capability structure -> `zpp-scaffold`;
- mixed, maintenance-oriented, or otherwise unspecialized ZPP product workflow ->
  `zpp-generic-workflow` at clarification;
- ungoverned artifact-only maintenance -> its owning artifact guidance;
- request that is not a ZPP product workflow or accepted direct artifact route ->
  `no-handoff`.

Ungoverned artifact-only maintenance is limited to repository README and reference
documentation, repository-local ZPP traits and context, and commit metadata. A
packaged workflow skill, packaged trait, canonical OpenSpec specification, artifact
loader, parser, validator, model conversion, or any artifact-backed executable or
public behavior is product work rather than a direct artifact route.

A missing specialized match is not evidence of product intent. Do not infer a store,
change, mutation authority, checkpoint authority, or later stage from repository
files or prior artifacts.

## 2. Resolve only classification evidence

When bounded read-only repository evidence can decide whether the request is a ZPP
product workflow, use `zpps-explore` with the exact roots and classification question,
consume only its observations, then repeat step 1 once. When the classification
depends on an outcome-changing owner decision, use `zpps-clarify` for that exact
decision and repeat step 1 once.

Do not explore or clarify indefinitely. If the result still does not positively
identify product-workflow shape or an accepted direct artifact route, select
`no-handoff`; do not use compatibility as a fallback.

## 3. Complete the selected route

For a selected `zpp-*` playbook, invoke it exactly once. This is an execution handoff,
not a recommendation or route report. Pass the original request, exact roots,
accepted classification evidence, accepted owner input, and only authority the owner
supplied. Preserve automatic progression, one-Clarify-gate best-decision delegation,
and persistent full authority as distinct facts; do not collapse or interpret them.
Invoking `zpp-auto` is not itself an automatic-progression grant. Do not select
`zpp-legacy-workflow`; that entry is eligible only through explicit owner invocation.
The selected complete playbook performs its mandatory workflow registration as its
first lifecycle action; triage neither pre-registers it nor bypasses that boundary.
Handoff does not satisfy the selected playbook's Clarify readiness or authorize
planning.

After a playbook invocation, transfer control and do not return to triage. Remain in
the same workflow invocation until the selected playbook returns an actual blocked or
completed lifecycle result. Naming, recommending, or acknowledging the route is not
a result and cannot terminate automatic execution.

For an accepted direct artifact route, invoke only its owning artifact guidance and
return that operation's actual result without creating workflow reminder state or
workflow-stage outcomes. For `no-handoff`, report that the request did not establish
a ZPP product workflow and perform no registration, workflow invocation, or governed
mutation.

No routed authority authorizes Git push, a GitHub merge action, or access to or
mutation of a cloud environment. Preserve the requirement for separate step-by-step
owner authorization when handing off any request that could reach those operations.

Never invoke the kernel directly, mutate governed artifacts during triage, add
authority, or claim completion on a selected playbook's behalf.
