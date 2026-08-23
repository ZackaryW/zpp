---
name: zpps-shape-bdd
description: Mutate BDD and trace artifacts for already accepted public behavior only when that exact shaping operation is explicitly requested; exclude requirement discovery.
---

# Shape behavior and BDD authority

## Admit behavior shaping

Admit this component only when an active playbook configures this exact shaping or
the caller explicitly requests the immediate mutation of BDD and trace artifacts for
accepted public behavior. A configured workflow stage may also request an
applicability result for an accepted contract with no observable obligation. Required
readiness includes the accepted contract, capability owner, provisional examples,
and current binding evidence. Unresolved behavior, ownership, repository, or
integration facts require separate exploration or clarification; an eventual
testable feature alone does not admit shaping.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-shape-bdd`, the `observed_immediate_operation`,
`missing_readiness`, and the `separately_eligible_operation`. Stop before the normal
procedure and never invoke the separately eligible component.

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository roots and capability owner, resolved
OpenSpec root, change name, provisional examples, and current binding evidence.
When observable obligations require mutation, also require a current kernel
assessment whose action is `shape-bdd`. Pass the exact roots and change names; the kernel invokes
ZPP runtime coordination and returns structured leased or explicitly authorized
bypass evidence. Do not resolve registration, manifest UUIDs, owner identity,
environment overrides, or bundle commands here. If the assessment is absent or
stale, return `kernel-assessment-required`; block on any runtime-reported coordination
conflict. Do not reject merely because the caller is not a playbook.

Classify each accepted obligation by public observability. Put public-system behavior
in one independently runnable `features/<capability>/` root with a capability-local
support entry point, delegated environment lifecycle, and thin scenario-selected
bindings. Keep pure-function case matrices in unit tests, retaining a public BDD
scenario only when needed to prove system enforcement. Keep non-observable policy as
normative specification content; never fabricate BDD for it.

When classification finds no public-system obligation requiring an executable
feature contract, return `skipped: not applicable` with the classification evidence.
This verified no-op requires no mutation guard and changes no artifact.

Transfer every concrete executable OpenSpec example to the feature root. Immediately
above each scenario, write compact JSON with exactly these ordered keys:

```gherkin
# zpp-spec: {"root":"<root-id>","capability":"<capability-id>","requirement":"<exact-requirement-heading>","feature":"<git-root-relative-feature-path>","scenario":"<exact-scenario-name>"}
```

Use `store:<uuid>` only for the exact UUID returned by the public registered-store
list. Otherwise use `repo:<git-root-relative-path-to-openspec-root>` with forward
slashes. Never mint or infer a UUID. Replace the OpenSpec concrete example with a
trace-only conformance scenario carrying the identical five values and naming the
exact `<feature>::<scenario>` target; do not repeat executable steps there.

Require every binding to resolve uniquely in both directions and every scenario to
exercise the named behavior through the public system. Recorder-only steps, wording
assertions, and a shared capability-wide assertion block are not acceptance evidence.
Run the capability feature root independently and preserve relevant RED. After every
required edit and that evidence succeed, update only supplied OpenSpec tasks whose
text and scope are each fully satisfied by this shaping result. Never mark a partial,
adjacent, inferred, or unrelated task complete; omit task mutation when no matching
task record was supplied.

Return `completed`, `skipped: not applicable`, or `blocked`, with `kernel-assessment-required` or
`coordination-conflict` when that is the blocking reason, plus classifications, exact
bindings, changed paths, and RED evidence. Never
invoke another `zpps-*` skill, implement product behavior, select workflow
continuation, expand the lease, checkpoint, or claim lifecycle completion.
