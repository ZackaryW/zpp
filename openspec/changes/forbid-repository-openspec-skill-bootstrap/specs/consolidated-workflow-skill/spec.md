## ADDED Requirements

### Requirement: Consume only ZPP-provisioned OpenSpec operation skills
The consolidated workflow skill SHALL consume the exact installed
`openspec-explore`, `openspec-propose`, `openspec-update-change`,
`openspec-apply-change`, `openspec-sync-specs`, and `openspec-archive-change`
operation skills supplied by the initialized ZPP agent integration. During a
workflow run it SHALL NOT invoke or authorize `openspec init`, generate or vendor
an OpenSpec skill tree, install or project an OpenSpec operation skill, repair an
operation skill, or create a substitute operation owner in the target repository
or any other location.

When an operation required by the current stage is absent, unreadable, invalid,
stale, or requires local initialization, the workflow SHALL leave the stage
blocked, identify the exact operation skill, and direct the owner to root
`zpp init` for an uninitialized agent integration or root `zpp sync` for an
existing integration. The workflow SHALL NOT invoke either lifecycle command on
the owner's behalf.

This prohibition SHALL NOT prevent an installed operation skill from creating,
updating, validating, synchronizing, or archiving ordinary repo-local OpenSpec
planning artifacts under `openspec/`. Planning state SHALL NOT be treated as an
operation-skill installation.

#### Scenario: Use an installed operation owner
- **WHEN** an eligible workflow stage requires an OpenSpec operation and its exact ZPP-provisioned skill is available
- **THEN** the workflow follows that installed skill without invoking OpenSpec initialization or changing any skill installation

#### Scenario: Block a missing operation owner
- **WHEN** the exact OpenSpec operation skill required by the current stage is absent or invalid
- **THEN** the workflow leaves the stage blocked, identifies the skill, and directs the owner to the appropriate ZPP initialization or synchronization command without invoking it

#### Scenario: Reject a local initialization prerequisite
- **WHEN** an operation path proposes `openspec init`, a generated local skill tree, or project-scope operation-skill projection as a prerequisite
- **THEN** the workflow rejects that path and does not create, copy, install, project, or repair an OpenSpec operation skill anywhere

#### Scenario: Preserve repository planning operations
- **WHEN** an installed OpenSpec operation skill creates or updates proposal, change, specification, task, validation, synchronization, or archive state under the repository's `openspec/` directory
- **THEN** the workflow treats that state as allowed product planning rather than prohibited skill bootstrap
