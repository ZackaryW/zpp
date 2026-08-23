---
name: zpps-shape-bdd
description: Shape accepted public behavior into independently runnable capability BDD with one executable authority, from playbook or direct explicit configuration.
---

# Shape behavior and BDD authority

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository roots and capability owner, resolved
OpenSpec root, change name, provisional examples, and current binding evidence.
Because shaping mutates governed artifacts, also require a current kernel assessment
whose action is `shape-bdd`. Pass the exact roots and change names; the kernel invokes
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

Return `completed` or `blocked`, with `kernel-assessment-required` or
`coordination-conflict` when that is the blocking reason, plus classifications, exact
bindings, changed paths, and RED evidence. Never
invoke another `zpps-*` skill, implement product behavior, select workflow
continuation, expand the lease, checkpoint, or claim lifecycle completion.
