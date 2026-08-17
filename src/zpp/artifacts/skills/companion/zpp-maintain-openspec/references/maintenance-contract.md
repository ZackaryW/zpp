# OpenSpec maintenance contract

Apply this contract before changing a canonical specification or deleting an archived change.

## Audit record

Record one row per exact archived-change path with these fields:

| Field | Required evidence |
| --- | --- |
| Exact path | Resolved path below the active OpenSpec archive root |
| Capabilities | Every capability delta carried by the archive |
| Canonical coverage | Destination requirement and scenario for every delta requirement and scenario |
| Unique content | Accepted proposal, design, task, requirement, scenario, or decision not represented elsewhere |
| Contradictions | Conflicting normative constraint, scenario, serialization, owner boundary, or policy |
| Task state | Complete, intentionally deferred with accepted disposition, or unresolved |
| Git recoverability | Exact path and content recoverable from inspected Git history |
| Validation | Current strict OpenSpec result and the revision it covers |
| Outcome | `eligible`, `blocked`, or `retained` |
| Reason | Concrete evidence supporting the outcome |

Do not collapse candidates into a directory-wide conclusion. Evidence may differ between archives from the same day or capability.

## Eligibility matrix

Mark an archive `eligible` only when all conditions are true:

- it is an archived change, not active planning state;
- every delta requirement and scenario has an unambiguous current canonical destination;
- no accepted proposal, design, task, requirement, scenario, or decision remains unique;
- tasks are complete or carry an accepted explicit disposition;
- no unresolved contradiction or ownership ambiguity remains;
- strict validation passes for the reconciled canonical state;
- Git can recover the exact archived path and inspected content;
- the audit evidence still matches the working tree.

Mark it `blocked` when a condition might become true after reconciliation or an owner decision. Name the missing evidence or decision. Mark it `retained` when it is active, intentionally preserved, outside scope, or carries unique historical content the owner wants available in-tree.

Never use age, naming convention, apparent duplication, completed checkboxes, successful validation, or Git recoverability alone as eligibility proof.

## Consolidation mapping

Before editing, record one mapping per source requirement:

| Field | Required content |
| --- | --- |
| Source | Capability, requirement heading, and all scenario headings |
| Destination | Exact canonical capability and requirement heading |
| Preserved contract | Normative clauses, constraints, scenarios, and owner boundary retained |
| Difference | Every semantic difference, including stronger or weaker language |
| Resolution | Current authority or explicit owner decision resolving each difference |
| Proposed removal | Exact duplicated requirement or capability path, if any |

A consolidation is lossless only when every accepted source clause and scenario survives at an explicit destination. Similar wording is not semantic equivalence. If the mapping depends on a new product choice, stop and expose it under `Unresolved — Do Not Assume` in the active workflow change.

## Mutation sequence

1. Complete the read-only audit and consolidation mapping.
2. Revalidate evidence immediately before mutation.
3. Reconcile canonical specifications through the explicit `zpp-workflow` change and exact installed OpenSpec operations.
4. Run strict validation and inspect the full canonical diff.
5. Present only currently eligible exact archive paths.
6. Obtain owner authorization naming each path.
7. Reconfirm the authorized set is unchanged and contained by the archive root.
8. Remove only the authorized exact paths.
9. Show the deletion diff and rerun strict validation.
10. Use `zmem-author-commits` for an authorized commit and inspect the resulting commit with `zmem show`.

Canonical reconciliation authority, exact-path deletion authority, and commit authority are separate. One never implies another.
