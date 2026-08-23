---
name: zpps-planning-ponytail
description: Plan resolved utility responsibilities with the Ponytail ladder, read-only unless an exact planning write is requested; explore unknown dependency evidence first.
---

# Plan utilities with Ponytail

## Admit utility planning

Admit this component only when an active playbook configures this exact utility plan
or the caller's immediate operation is to plan utility boundaries for accepted,
shaped behavior. Required readiness includes the accepted responsibility and the
dependency evidence needed to apply the ladder. A read-only plan needs no mutation
intent; writing a planning artifact additionally requires explicit intent for that
exact write or exact playbook configuration. Unknown package, API, repository, or
integration facts belong to `zpps-explore` before utility planning.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-planning-ponytail`, the
`observed_immediate_operation`, `missing_readiness`, and the
`separately_eligible_operation`. Stop before the normal procedure and never invoke
the separately eligible component.

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository roots, shaped behavior and binding
inventory, dependency evidence, and any predecessor outcome relevant to utility
planning. This procedure is read-only unless the caller explicitly asks it to write a
planning artifact. For such a write, require a current kernel assessment with a
matching action for the exact root and change name. The kernel invokes ZPP runtime
coordination and returns structured leased or explicitly authorized bypass evidence.
Do not resolve registration, manifest UUIDs, owner identity, environment overrides,
or bundle commands here. Otherwise return `kernel-assessment-required` or
`coordination-conflict` with the unresolved targets.

For each proposed utility responsibility, apply these rungs in order:

1. Confirm the responsibility is required by accepted behavior.
2. Reuse suitable repository code.
3. Use the standard library.
4. Use the native platform.
5. Use an already installed dependency.
6. Write the minimum repository-owned code.

When a confirmed non-trivial responsibility survives those rungs, compare maintained
packages by maturity, integration cost, security and maintenance fit, and the
proportion of their surface actually required. Use no universal percentage threshold.

Produce a disposable signature-level plan naming ownership, inputs, outputs, failure
contracts, seams, dependency decisions, and verification intent. Return `completed`,
`blocked`, or `skipped: not applicable`, with `kernel-assessment-required` or
`coordination-conflict` when that is the blocking reason, plus the ladder evidence
and any changed planning paths. A skip is truthful
only when the complete accepted behavior needs no
utility change. When this skill writes a governed task artifact, update only supplied
planning tasks whose text and scope are each fully satisfied by the completed
Ponytail plan. Never mark a partial, implementation, adjacent, inferred, or unrelated
task complete.

Never invoke another `zpps-*` skill, implement utilities, select workflow
continuation, mutate OpenSpec incidentally, expand a lease, checkpoint, or claim
lifecycle completion.
