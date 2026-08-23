# openspec-maintenance-skill Specification

## Purpose

Define the packaged manual guidance and safety gates for auditing legacy OpenSpec changes, consolidating canonical specifications without semantic loss, and selectively removing eligible archived paths.

## Requirements

### Requirement: Packaged manual OpenSpec maintenance guidance
ZPP SHALL package `zpp-maintain-openspec` as a companion skill that guides an agent to audit legacy archived changes, consolidate overlapping canonical specifications, and remove only eligible authorized archive paths. The skill SHALL run only for an explicit request, SHALL introduce no ZPP command or automatic hook, and SHALL NOT infer workflow-stage, commit, or deletion authority from repository detection, archive age, a recommendation, or automatic workflow progression.

The skill SHALL treat canonical OpenSpec specifications and accepted owner input as current authority and archived changes as provenance evidence rather than current authority. Any canonical specification edit SHALL remain governed by an explicitly invoked current complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) at `clarify`, or by existing owner-authorized end-to-end playbook execution, together with the exact installed ZPP-owned `zpps-*` adapter for each OpenSpec operation. The companion skill SHALL NOT select or advance that playbook sequence itself.

#### Scenario: Leave maintenance dormant without a request
- **WHEN** an installed agent starts a session, detects an OpenSpec directory, or runs an unrelated workflow change
- **THEN** the maintenance skill does not audit, consolidate, delete, commit, or advance workflow state

#### Scenario: Preserve operation ownership
- **WHEN** a requested maintenance outcome requires canonical edits, synchronization, archival, or commits
- **THEN** the skill directs each operation through its exact current playbook, ZPP-owned adapter, or zmem owner without creating or initializing a repository-local substitute

### Requirement: Evidence-backed archive audit
Before recommending mutation, the maintenance skill SHALL inspect active changes, canonical specifications, archived deltas and tasks, relevant Git provenance, and valid zmem evidence. It SHALL classify each accepted archive item by preservation authority: current behavior, constraints, scenarios, serialization, and owner boundaries SHALL have an unambiguous canonical OpenSpec destination; historical rationale and superseded decisions SHALL have traceable zmem representation. The appropriate one of those preservation sources SHALL be sufficient, and the audit SHALL NOT require every planning sentence to be duplicated across both stores or treat a stale task checkbox as an independent blocker when current repository evidence proves the represented outcome.

The skill SHALL expose partial preservation, contradictions, ambiguous ownership, and unresolved current behavior. It SHALL NOT treat zmem as a substitute for missing current normative behavior or settle an outcome-changing difference by recency or inference.

The skill SHALL report an executive summary and exact next actions before its detailed per-path evidence. The detailed record SHALL identify each exact archive path, affected capabilities, preservation mapping, supersession age where applicable, contradictions, zmem effects, Git recoverability, eligibility outcome, and blocking reason.

#### Scenario: Preserve an archive through the appropriate authority
- **WHEN** every current normative item in an archive is represented canonically and every historical or superseded decision is represented in zmem
- **THEN** the audit treats preservation as complete without requiring each item to appear in both stores or duplicating unrelated planning prose

#### Scenario: Reject memory-only current behavior
- **WHEN** an archive contains current accepted behavior that exists only in zmem
- **THEN** the audit blocks removal until that behavior has an unambiguous canonical OpenSpec destination

#### Scenario: Lead with actionable results
- **WHEN** the audit completes
- **THEN** it reports concise counts and exact next actions before the detailed candidate table and mappings

### Requirement: Lossless canonical consolidation plan
When canonical requirements govern the same behavior under the same owner boundary, the maintenance skill SHALL produce an explicit before-and-after mapping and reconcile them into one authoritative canonical destination before archive removal. The mapping SHALL preserve every mutually accepted current constraint and scenario, identify superseded or conflicting clauses, and remove redundant requirements or capability files only after their current contract is represented by the destination.

The skill SHALL NOT merge requirements merely because they mention the same component, retain a stronger phrase that conflicts with current accepted policy, weaken accepted behavior silently, or invent product policy. A semantic difference or owner-boundary ambiguity SHALL block consolidation until the owner resolves it.

#### Scenario: Merge requirements governing the same behavior
- **WHEN** two canonical requirements govern the same behavior and owner boundary without an unresolved semantic difference
- **THEN** the skill maps their accepted constraints and scenarios into one authoritative destination and proposes removal of the redundant source

#### Scenario: Keep distinct component concerns separate
- **WHEN** requirements mention the same component but govern different operations or owner boundaries
- **THEN** the skill leaves them separate rather than consolidating by terminology alone

#### Scenario: Refuse a conflicting strongest clause
- **WHEN** one source contains stronger wording that conflicts with current accepted policy
- **THEN** the skill exposes the conflict instead of automatically retaining that clause as the consolidated contract

### Requirement: Exact-path archive removal gate
The maintenance skill SHALL recommend immediate removal of a non-superseded archived change when every accepted item is preserved by its appropriate canonical OpenSpec or zmem authority and no unresolved current behavior, contradiction, or ownership ambiguity remains. Stale task bookkeeping and unique wording that carries no unpreserved accepted behavior or decision SHALL NOT block removal.

For outdated or superseded specification or archive content, the skill SHALL additionally require the capability-relative ten-version grace period defined by this capability. The skill SHALL perform no archive deletion before required canonical consolidation, zmem effects, and strict OpenSpec validation succeed. It SHALL require explicit owner authorization naming every exact archive path, remove only those eligible paths, show the deletion diff, validate again, and use `zmem-author-commits` before committing when separate commit authority exists. It SHALL NOT use a broad recursive target, delete an active change, or widen authorized paths by inference.

#### Scenario: Remove a completely preserved redundant archive
- **WHEN** a non-superseded archived change is completely preserved by the appropriate canonical or zmem authority and has no unresolved conflict
- **THEN** the skill marks its exact path eligible without imposing the supersession grace period or additional planning-prose duplication

#### Scenario: Require exact deletion authority
- **WHEN** an audit identifies one or more eligible archived changes
- **THEN** the skill presents their exact paths and waits for owner authorization that names those paths before deleting anything

#### Scenario: Remove only validated authorized candidates
- **WHEN** required reconciliation and validation succeed and the owner authorizes exact eligible archive paths
- **THEN** the skill removes only those paths, presents the deletion diff, revalidates the repository, and leaves every other archive untouched

### Requirement: Capability-relative supersession and zmem cancellation
One supersession version SHALL mean one later committed archived change whose delta contains the same capability. The maintenance skill SHALL order versions by the Git commits that archived the changes rather than by directory name, filename date, project release, or arbitrary commit count. A superseded specification or archive item SHALL become removal-eligible only after ten later archived changes affect that item’s capability. A multi-capability archive SHALL remain ineligible until every superseded item satisfies its own capability count.

When current canonical authority or an explicit owner decision proves a valid zmem `DECISION` fully superseded, the skill SHALL resolve its exact SHA and one-based annotation index and use `zmem-author-commits` to create a validated `zmem(CANCEL)[sha, index]` effect without waiting for the archive grace period. It SHALL use deep replay for validation. It SHALL NOT cancel a lesson, a partially valid decision, or an unresolved conflict; a still-partly-valid decision SHALL remain eligible for deliberate decay instead.

#### Scenario: Count ten later capability versions
- **WHEN** a superseded archived item belongs to one capability
- **THEN** the skill counts later Git-ordered archived changes containing that capability and permits removal only after the count reaches ten

#### Scenario: Age every superseded item in a multi-capability archive
- **WHEN** one archived change contains superseded items from several capabilities
- **THEN** the skill keeps the archive until every superseded item has ten later archived changes affecting its own capability

#### Scenario: Cancel a fully superseded decision immediately
- **WHEN** current authority proves an earlier valid zmem decision fully invalid
- **THEN** the skill resolves the exact entry, validates a `CANCEL` effect with deep replay, and stops that decision from remaining valid without waiting for archive expiration

#### Scenario: Preserve a partially valid memory
- **WHEN** an earlier zmem decision remains partly valid or its supersession is unresolved
- **THEN** the skill does not cancel it and instead retains it or proposes deliberate decay with the unresolved difference exposed

### Requirement: No repository-local OpenSpec skill bootstrap
During maintenance, the skill SHALL use only the already installed ZPP-owned `zpps-explore`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-sync-specs`, `zpps-verify-change`, and `zpps-archive-change` adapters when their bounded operations are needed. It SHALL never invoke a generated `openspec-*` operation skill as authority, invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or project an operation skill, repair one, or create a substitute operation owner in the target repository or another location.

When a required ZPP-owned adapter is absent, unreadable, invalid, stale, or requests local initialization, the skill SHALL block that operation and direct the owner to root `zpp init` when no ZPP integration exists or root `zpp sync` when one already exists. It SHALL never run those user-scope lifecycle commands on the owner's behalf.

#### Scenario: Block maintenance when an operation owner is missing
- **WHEN** an eligible maintenance step requires an unavailable or unusable ZPP-owned OpenSpec adapter
- **THEN** the skill leaves the step blocked, names the exact missing skill, and performs no local OpenSpec skill bootstrap or substitute operation

### Requirement: BDD-target scenario reconciliation
The OpenSpec maintenance skill SHALL compare canonical OpenSpec scenarios with established BDD feature scenarios before consolidating or removing scenario content. It SHALL replace a duplicated OpenSpec scenario body with an exact target-form scenario only when `features/<capability>/<capability>.feature::<scenario name>` belongs to the same capability owner, traces to the requirement, exists exactly, has scenario-selected executable public-system bindings, and passes relevant verification. The retained target-form scenario SHALL identify the exact feature authority and SHALL NOT repeat its executable steps.

The maintenance skill SHALL preserve every complete OpenSpec scenario that lacks qualifying BDD coverage. It SHALL treat a missing, stale, cross-capability, untraced, recorder-only, capability-wide, wording-only, or unverified feature target as a blocker, and SHALL NOT infer coverage from similar names or prose. Archive preservation mapping SHALL treat verified target-form scenarios as canonical trace plus feature-owned executable behavior and SHALL treat neither source alone as complete.

#### Scenario: Reconcile a covered scenario to its BDD target
- **WHEN** a canonical OpenSpec scenario duplicates behavior verified by an exact same-capability feature scenario and its scenario-selected binding
- **THEN** maintenance replaces the duplicated steps with a target-form scenario naming that exact feature target

#### Scenario: Preserve an uncovered OpenSpec scenario
- **WHEN** a canonical OpenSpec scenario has no qualifying BDD feature target
- **THEN** maintenance retains its complete WHEN/THEN content and does not remove or redirect it

#### Scenario: Reject guessed or insufficient coverage
- **WHEN** a possible feature target matches only by terminology, belongs to another capability, lacks requirement traceability, uses a recorder or capability-wide assertion, or has not passed relevant verification
- **THEN** maintenance leaves the OpenSpec scenario unchanged and reports the exact coverage blocker

#### Scenario: Preserve a targeted archive scenario completely
- **WHEN** an archived current scenario maps to a canonical target-form scenario whose exact BDD feature remains valid and verified
- **THEN** maintenance treats the canonical trace and feature-owned executable behavior together as complete preservation
