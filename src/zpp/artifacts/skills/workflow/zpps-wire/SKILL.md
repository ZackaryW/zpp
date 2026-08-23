---
name: zpps-wire
description: Mutate a resolved public composition boundary to connect accepted behavior and proven utilities only when that exact wiring is explicitly requested.
---

# Wire public behavior

## Admit public composition wiring

Admit this component only when an active playbook configures this exact wiring or the
caller explicitly requests the immediate mutation of a resolved public composition
boundary. Required readiness includes accepted behavior, approved feature bindings,
proven utilities, and an identified composition owner. Unknown integration owners,
APIs, repositories, or composition choices require separate exploration; unproven
utilities and unaccepted design changes do not admit wiring.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-wire`, the `observed_immediate_operation`,
`missing_readiness`, and the `separately_eligible_operation`. Stop before the normal
procedure and never invoke the separately eligible component.

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository roots, approved feature and binding
inventory, verified utility evidence, resolved public composition owner, and a
current kernel assessment for every exact root and change target. The kernel invokes
ZPP runtime coordination and returns structured leased or explicitly authorized
bypass evidence. Do not resolve registration, manifest UUIDs, owner identity,
environment overrides, or bundle commands here. If the guard is absent or stale,
return `kernel-assessment-required`; block on any runtime-reported coordination
conflict. Do not reject a direct caller merely for being direct.

Reconcile the proposed composition with current public entry points. Bind each
approved feature scenario through the actual application or composition owner. Keep
Behave bindings thin and scenario-selected: reusable support may orchestrate the
public system but cannot replace scenario-specific verification. In a monorepo, keep
public acceptance at the owning application and focused utility tests in reusable
packages.

Run focused composition verification for every changed binding and preserve the
scenario-specific result. Stop with `blocked` when the expected public owner is
missing, utility evidence is stale, or wiring would require an unaccepted design
change.

After every required wiring edit and its focused evidence succeed, update only
supplied OpenSpec tasks whose text and scope are each fully satisfied by this wiring
result. Never mark a partial, adjacent, inferred, or unrelated task complete.

Return `completed` or `blocked`, with `kernel-assessment-required` or
`coordination-conflict` when that is the blocking reason, plus changed paths,
exact public bindings, verification evidence, and any
design contradiction. Never invoke another `zpps-*` skill, invent policy, redesign
utilities, form specifications, select continuation, expand the lease, checkpoint,
or claim lifecycle completion.
