---
name: zpps-form-specs
description: Audit OpenSpec and BDD authority, prepare trace-only specification form, and signal required canonical synchronization without invoking it.
---

# Form specifications without duplicate acceptance authority

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository and OpenSpec roots, resolved store and
change identities, current binding inventory, mature GREEN evidence, and canonical
and delta paths reported by OpenSpec. For edits, also require a current kernel
assessment for the exact roots and change names. The kernel invokes ZPP runtime
coordination and returns structured leased or explicitly authorized bypass evidence.
Do not resolve registration, manifest UUIDs, owner identity, environment overrides,
or bundle commands here. If absent or mismatched, return
`kernel-assessment-required` or `coordination-conflict` with the precise unresolved
inputs. A prior playbook delegation is not required.

Resolve every OpenSpec-to-feature binding in both directions. Each executable
obligation must have one or more scenario-selected public-system feature authorities
and no semantically equivalent concrete OpenSpec example. A specification-only
obligation must have no feature claiming executable authority. Reject stale,
cross-capability, unverified, recorder-only, wording-only, or orphaned bindings.

Require the feature-side `# zpp-spec:` declaration and the OpenSpec trace-only
conformance scenario to contain identical compact JSON with ordered `root`,
`capability`, `requirement`, `feature`, and `scenario` keys. Use `store:<uuid>` only
for an exact discovered registered-store UUID; otherwise use a normalized
`repo:<git-root-relative-path-to-openspec-root>`. Require the feature path and
scenario title to resolve uniquely, and name the exact `<feature>::<scenario>` target
without restating executable steps in OpenSpec.

On the first pass, make only the allowed delta-spec authority corrections and perform
the semantic duplicate/orphan audit. If canonical deltas remain, return
`sync-required` with the exact selected delta paths, rules/input snapshot needs, and
pre-sync audit evidence. The caller must explicitly invoke `zpps-sync-specs` and then
re-enter this skill with the sync result. On re-entry, audit the resulting canonical
specifications and return `completed` only when every binding and authority resolves.
After all exact specification edits and the final audit succeed, update only supplied
OpenSpec tasks whose text and scope are each fully satisfied by this formation result.
Never mark a partial, adjacent, inferred, or unrelated task complete.

Return `completed`, `blocked`, or `sync-required`, with
`kernel-assessment-required` or `coordination-conflict` when that is the blocking
reason, plus changed paths
and the complete audit. Never invoke another `zpps-*` skill, perform canonical
synchronization, select continuation, expand a lease, checkpoint, archive, or claim
lifecycle completion.
