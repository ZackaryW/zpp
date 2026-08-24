---
name: zpp-legacy-workflow
description: Translate an explicitly invoked preceding generic ZPP workflow request exactly once into the current generic playbook.
---

# Translate one explicit legacy invocation

This entry is compatibility-only. Admit it only when the caller explicitly invokes
`zpp-legacy-workflow` with a request shaped for the immediately preceding
consolidated generic workflow. Automatic triage never selects this entry.

Preserve the original request, exact repository roots, accepted classification or
owner input, owner-authorized end-to-end mode when supplied, and only authority the
owner supplied. Invoke `zpp-generic-workflow` exactly once with that complete input,
then transfer control to it for the remainder of the workflow invocation.

Do not classify the outcome again, copy or execute a lifecycle stage, invoke a
`zpps-*` component, acquire a lease, mutate governed state, select continuation, add
authority, translate a ZPP 1.x `zpp-flow-*` identity, or claim the generic playbook's
blocked or completed result. If the request is not a supported explicit legacy
invocation, report `legacy-invocation-required` and perform no handoff.
