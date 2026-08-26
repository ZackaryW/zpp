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

Require the accepted contract revision, exact repository roots and capability owner, resolved
OpenSpec root, change name, provisional examples, and current binding evidence.
For observable mutation, obtain the kernel's `shape-bdd` pre-action assessment for
the exact roots and change names. Return `kernel-assessment-required` or
`coordination-conflict` before editing when it is absent, stale, or blocked.

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
slashes. Never mint or infer a UUID. After creating the bound feature scenario,
remove its corresponding OpenSpec scenario completely. Retain the normative OpenSpec
requirement, but do not create a concrete, trace-only, target-form, or other
surrogate scenario for behavior now owned by BDD.

Require every feature-side binding to resolve uniquely to its OpenSpec root,
capability, and requirement and every scenario to exercise the named behavior through
the public system. Literal-text matching, self-recording steps, execution-only checks,
pure occurrence or collection counts, and shared capability-wide assertions are not
acceptance evidence. A count may constrain an already observed behavioral outcome,
but it cannot be the scenario's sole public-system observation.
Run the capability feature root independently and preserve relevant RED. After every
required edit and that evidence succeed, update only supplied OpenSpec tasks whose
text and scope are each fully satisfied by this shaping result. Never mark a partial,
adjacent, inferred, or unrelated task complete; omit task mutation when no matching
task record was supplied.

Return `completed`, `skipped: not applicable`, or `blocked`, with
`kernel-assessment-required` or `coordination-conflict` when applicable, plus
classifications, exact bindings, changed paths, and RED evidence. Do not implement
product behavior in this stage.
