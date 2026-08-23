## MODIFIED Requirements

### Requirement: Explicit component delegation
A playbook SHALL invoke the exact configured ZPP phase or operation skill that owns each declared component use. A direct partial invocation MAY select the same component by supplying its required operation configuration. Before the first governed mutation for a change set, the playbook or directly invoked component SHALL pass the exact resolved repository roots and change names to `zpps-workflow-kernel`; the kernel SHALL invoke ZPP's runtime coordination operation and consume its structured guard without implementing registration, identity persistence, environment parsing, manifest preparation, or lease transitions in skill instructions. Missing internal store registration, store UUID, owner, or bundle identity SHALL trigger runtime preparation rather than an owner question. A preparation, override, or acquisition conflict SHALL remain blocked and visible. Repo-local roots remain valid for read-only work and existing `repo:` locator resolution. During finalization the kernel SHALL submit every exact changed path and archive result to that runtime operation, which audits paths, records archives, and completes the same bundle; changed paths SHALL NOT be bundle members. The component SHALL return its observed output and SHALL NOT select workflow continuation, advance the playbook sequence, expand the bundle, or claim lifecycle completion.

#### Scenario: Acquire without coordination questions
- **WHEN** an eligible phase has mutation authority and is about to perform the first governed OpenSpec mutation
- **THEN** the caller obtains the kernel's automatically prepared guard and exact Bundler bundle without asking the owner for registration, UUID, owner-string, or lease input

#### Scenario: Pause on a genuine coordination conflict
- **WHEN** automatic preparation or acquisition reports an ambiguous registration, invalid manifest, topology error, or incompatible retained bundle
- **THEN** the component remains blocked with the concrete conflict and does not bypass coordination safety

#### Scenario: Complete after every member archives
- **WHEN** `zpps-archive-change` or an authorized `zpps-bulk-archive-change` operation has returned every declared member archive and the path audit passes
- **THEN** the kernel records every archive and completes the bundle using the retained ZPP-managed owner

#### Scenario: Reject operation continuation
- **WHEN** a bounded operation returns successful evidence
- **THEN** the kernel may assess that evidence but does not choose a continuation, and the operation itself does not continue to another stage

### Requirement: Automatic Bundler workflow boundary
The packaged workflow family SHALL describe repository/change targets in ZPP terms, delegate automatic preparation and Bundler progression to ZPP's runtime through `zpps-workflow-kernel`, and never ask the owner to choose or type an OpenSpec store registration, store UUID, durable owner string, bundle UUID, environment override, or lease command during ordinary authorized execution. Skills SHALL neither parse `ZPP_WORKFLOW_COORDINATION` nor implement a bypass. They SHALL preserve explicit mutation, archive, and bypass authority, surface runtime coordination conflicts, and contain no OpenLease name, workspace-management delegation, session, claim, permit, successor, reconciliation, handoff, cleanup, or preparation-repair guidance.

#### Scenario: Inspect seamless workflow coordination guidance
- **WHEN** the packaged workflow family is inspected
- **THEN** it delegates registration, identity, override, and bundle progression to the ZPP runtime while preserving visible authority and conflict boundaries
