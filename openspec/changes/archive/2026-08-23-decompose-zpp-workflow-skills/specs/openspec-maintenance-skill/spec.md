## MODIFIED Requirements

### Requirement: Packaged manual OpenSpec maintenance guidance
ZPP SHALL package `zpp-maintain-openspec` as a companion skill that guides an agent to audit legacy archived changes, consolidate overlapping canonical specifications, and remove only eligible authorized archive paths. The skill SHALL run only for an explicit request, SHALL introduce no ZPP command or automatic hook, and SHALL NOT infer workflow-stage, commit, or deletion authority from repository detection, archive age, a recommendation, or automatic workflow progression.

The skill SHALL treat canonical OpenSpec specifications and accepted owner input as current authority and archived changes as provenance evidence rather than current authority. Any canonical specification edit SHALL remain governed by an explicitly invoked current complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) at `clarify`, or by existing owner-authorized end-to-end playbook execution, together with the exact installed ZPP-owned `zpps-*` adapter for each OpenSpec operation. The companion skill SHALL NOT select or advance that playbook sequence itself.

#### Scenario: Leave maintenance dormant without a request
- **WHEN** an installed agent starts a session, detects an OpenSpec directory, or runs an unrelated workflow change
- **THEN** the maintenance skill does not audit, consolidate, delete, commit, or advance workflow state

#### Scenario: Preserve operation ownership
- **WHEN** a requested maintenance outcome requires canonical edits, synchronization, archival, or commits
- **THEN** the skill directs each operation through its exact current playbook, ZPP-owned adapter, or zmem owner without creating or initializing a repository-local substitute

### Requirement: No repository-local OpenSpec skill bootstrap
During maintenance, the skill SHALL use only the already installed ZPP-owned `zpps-explore`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-sync-specs`, `zpps-verify-change`, and `zpps-archive-change` adapters when their bounded operations are needed. It SHALL never invoke a generated `openspec-*` operation skill as authority, invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or project an operation skill, repair one, or create a substitute operation owner in the target repository or another location.

When a required ZPP-owned adapter is absent, unreadable, invalid, stale, or requests local initialization, the skill SHALL block that operation and direct the owner to root `zpp init` when no ZPP integration exists or root `zpp sync` when one already exists. It SHALL never run those user-scope lifecycle commands on the owner's behalf.

#### Scenario: Block maintenance when an operation owner is missing
- **WHEN** an eligible maintenance step requires an unavailable or unusable ZPP-owned OpenSpec adapter
- **THEN** the skill leaves the step blocked, names the exact missing skill, and performs no local OpenSpec skill bootstrap or substitute operation
