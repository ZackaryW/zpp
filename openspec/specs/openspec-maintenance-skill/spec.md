# openspec-maintenance-skill Specification

## Purpose

Define the packaged manual guidance and safety gates for auditing legacy OpenSpec changes, consolidating canonical specifications without semantic loss, and selectively removing eligible archived paths.

## Requirements

### Requirement: Packaged manual OpenSpec maintenance guidance
ZPP SHALL package `zpp-maintain-openspec` as a companion skill that guides an agent to audit legacy archived changes, consolidate overlapping canonical specifications, and remove only eligible authorized archive paths. The skill SHALL run only for an explicit request, SHALL introduce no ZPP command or automatic hook, and SHALL NOT infer workflow-stage, commit, or deletion authority from repository detection, archive age, a recommendation, or automatic workflow progression.

The skill SHALL treat canonical OpenSpec specifications and accepted owner input as current authority and archived changes as provenance evidence rather than current authority. Any canonical specification edit SHALL remain governed by an explicitly invoked `zpp-workflow` change and its installed OpenSpec operation skills.

#### Scenario: Leave maintenance dormant without a request
- **WHEN** an installed agent starts a session, detects an OpenSpec directory, or runs an unrelated workflow change
- **THEN** the maintenance skill does not audit, consolidate, delete, commit, or advance workflow state

#### Scenario: Preserve operation ownership
- **WHEN** a requested maintenance outcome requires canonical edits, synchronization, archival, or commits
- **THEN** the skill directs each operation through its exact installed workflow, OpenSpec, or zmem owner without creating or initializing a repository-local substitute

### Requirement: Evidence-backed archive audit
Before recommending mutation, the maintenance skill SHALL inspect active changes, canonical specifications, archived deltas and tasks, relevant Git provenance, and valid zmem evidence. It SHALL produce a candidate table identifying each exact archive path, affected capabilities, canonical requirement-and-scenario coverage, unique or unresolved content, contradictions, task state, Git recoverability, eligibility outcome, and blocking reason.

An archive SHALL remain retained when it is active, partially synchronized, ambiguously owned, contradicted, missing recoverable provenance, or contains unique accepted behavior, scenarios, decisions, or unresolved task state. The skill SHALL expose an outcome-changing contradiction or ownership ambiguity to the owner instead of resolving it by recency or inference.

#### Scenario: Block a partially represented archive
- **WHEN** any archived requirement, scenario, accepted decision, or unresolved task state lacks an unambiguous canonical destination
- **THEN** the audit marks the exact archive path blocked and identifies the missing or conflicting coverage

#### Scenario: Distinguish provenance from authority
- **WHEN** an archived change conflicts with a current canonical requirement
- **THEN** the skill treats the archive as historical evidence, checks valid zmem and Git provenance, and requests an owner decision when current authority does not resolve the conflict

### Requirement: Lossless canonical consolidation plan
Before consolidating canonical specifications, the maintenance skill SHALL produce an explicit before-and-after mapping from every source requirement and scenario to its destination. The plan SHALL identify preserved normative constraints, scenario coverage, ownership moves, contradiction resolutions, and proposed removals.

The skill SHALL consolidate only genuine duplication or accepted ownership changes. It SHALL preserve every accepted constraint and scenario, SHALL NOT weaken normative language silently, SHALL NOT invent product policy, and SHALL NOT merge distinct requirements merely to reduce file count.

#### Scenario: Consolidate overlapping requirements safely
- **WHEN** current evidence proves that canonical requirements overlap and the owner has resolved any outcome-changing difference
- **THEN** the plan maps all accepted constraints and scenarios to one explicit canonical destination without semantic loss

#### Scenario: Refuse ambiguous consolidation
- **WHEN** two requirements appear similar but differ in an unresolved constraint, scenario, or owner boundary
- **THEN** the skill leaves both requirements unchanged and exposes the exact decision needed from the owner

### Requirement: Exact-path archive removal gate
The maintenance skill SHALL recommend archive removal only when every delta requirement and scenario is fully represented by validated canonical specifications, no unique accepted content or unresolved task state remains, and Git can recover the exact archived path. Git recoverability SHALL be necessary provenance evidence but SHALL NOT by itself establish semantic eligibility.

The skill SHALL perform no archive deletion before canonical reconciliation and strict OpenSpec validation succeed. It SHALL require explicit owner authorization naming every exact archive path, remove only those eligible paths, show the deletion diff, validate again, and use `zmem-author-commits` before committing when separate commit authority exists. It SHALL NOT use a broad recursive target, delete an active change, or widen authorized paths by inference.

#### Scenario: Require exact deletion authority
- **WHEN** an audit identifies one or more semantically eligible archived changes
- **THEN** the skill presents their exact paths and waits for owner authorization that names those paths before deleting anything

#### Scenario: Reject recoverability-only deletion
- **WHEN** Git can recover an archive but canonical coverage or unique-content checks are incomplete
- **THEN** the skill retains the archive and reports the incomplete semantic gate

#### Scenario: Remove only validated authorized candidates
- **WHEN** canonical reconciliation and strict validation succeed and the owner authorizes exact eligible archive paths
- **THEN** the skill removes only those paths, presents the deletion diff, revalidates the repository, and leaves every other archive untouched

### Requirement: No repository-local OpenSpec skill bootstrap
During maintenance, the skill SHALL use only already installed `openspec-explore`, `openspec-propose`, `openspec-update-change`, `openspec-apply-change`, `openspec-sync-specs`, and `openspec-archive-change` operation skills when their owned operations are needed. It SHALL never invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or project an operation skill, repair one, or create a substitute operation owner in the target repository or another location.

When a required operation skill is absent, unreadable, invalid, stale, or requests local initialization, the skill SHALL block that operation and direct the owner to root `zpp init` when no ZPP integration exists or root `zpp sync` when one already exists. It SHALL never run those user-scope lifecycle commands on the owner's behalf.

#### Scenario: Block maintenance when an operation owner is missing
- **WHEN** an eligible maintenance step requires an unavailable or unusable OpenSpec operation skill
- **THEN** the skill leaves the step blocked, names the exact missing skill, and performs no local OpenSpec skill bootstrap or substitute operation
