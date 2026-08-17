## Context

The consolidated workflow currently names OpenLease at its general operation boundary and directly owns retained-successor language during finalization, while agents have no dedicated ZPP skill for the provider's cross-repository command lifecycle. Separately, executable behavior can be described both as Gherkin under `features/` and as copied WHEN/THEN content in canonical OpenSpec scenarios. OpenSpec requires each added or modified requirement to retain at least one scenario block, so covered content needs a trace representation rather than removal without replacement.

## Goals / Non-Goals

**Goals:**

- Give cross-repository workspace operations one manually invoked companion skill with exact command, state-root, authority, and cleanup boundaries.
- Keep the general workflow provider-neutral and make it delegate workspace operations explicitly.
- Make an exact BDD feature scenario the executable authority when coverage is proven, while retaining a valid OpenSpec scenario block as its trace target.
- Preserve complete non-BDD OpenSpec scenarios and block stale, unbound, cross-capability, or unverified feature targets.

**Non-Goals:**

- Add or mirror an OpenLease lifecycle under the `zpp` CLI.
- Change OpenLease, Agent Router, or ZPP implementation logic; the existing discovered companion inventory will include the new skill.
- Bulk-migrate every existing canonical scenario in this change.
- Treat filename similarity, matching prose, or a passing capability-wide assertion as BDD coverage.

## Decisions

### One dedicated workspace operation owner

Package `zpp-workspace-management` in the companion role. The general workflow names this skill whenever it needs cross-repository topology, workspace lifecycle, locking, successor handling, reconciliation, handoff, abandonment, or cleanup. The companion skill may invoke the installed OpenLease CLI internally, but it does not become a workflow stage authority and introduces no ZPP command.

This keeps exact provider commands out of the general workflow without creating a façade that would duplicate the provider's lifecycle. The alternative—adding `zpp workspace`—was rejected because the owner selected existing internal commands and the canonical command hierarchy currently forbids a mirrored space lifecycle.

### Exact selected-home state root

The workspace skill resolves the selected ZPP home from an explicit owner value or the documented `~/.zpp` default and supplies its exact `openlease` child as the provider state root. It inspects installed command help and current topology before prescribing operations, uses explicit identifiers and repository paths, and never relies on ambient selection when a durable mutation is proposed.

### Separate observation from mutation

Status, topology inspection, planning, and lockability checks are read-only. Registration, relationships, workspace creation or association, locking, successor creation, reconciliation application, release, finalization, handoff, abandonment, recovery, and cleanup require the authority appropriate to their exact targets. Workflow progression does not supply provider callback choice, conflict resolution, reconciliation, or destructive cleanup authority.

### BDD-target scenario representation

A BDD-covered OpenSpec scenario becomes a target-form scenario instead of being deleted outright:

```markdown
#### Scenario: BDD target — <scenario name>
- **WHEN** executable behavior is covered by `features/<capability>/<capability>.feature::<scenario name>`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
```

The target is eligible only when the feature belongs to the same capability owner, the exact scenario exists, its bindings select and exercise the behavior it names through the public system, the scenario traces to the requirement, and relevant verification passes. A recorder step, capability-wide assertion, wording assertion, unverified target, or semantic guess is not coverage.

Every scenario without qualifying BDD coverage remains a complete OpenSpec WHEN/THEN scenario. If a target becomes stale or loses valid binding, workflow formation and maintenance block rather than silently discarding the normative case.

### No automatic historical migration

This change installs the ownership rule and the skills that enforce it. Existing canonical scenarios are migrated only through a later evidence-backed workflow or maintenance invocation so semantic coverage is assessed rather than inferred from names.

## Risks / Trade-offs

- **Target paths or scenario names can drift** → Revalidate exact targets and bindings whenever specs are formed or maintained; block stale targets.
- **A trace scenario is less self-contained than copied steps** → Keep the normative requirement text and exact feature target together, while making the executable feature the single scenario body.
- **Provider commands may evolve independently** → Discover the installed command surface before use and never invent command text.
- **Workspace cleanup can affect several repositories** → Require exact identifiers, paths, observed state, and operation-specific authority before mutation.
