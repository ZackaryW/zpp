## MODIFIED Requirements

### Requirement: Permanent workflow bundle ownership
ZPP SHALL package the twelve permanent `zpp-*` workflow skills as one versioned owned bundle. Installed copies SHALL be projections of the packaged bundle, preserve every required skill resource, and SHALL NOT embed agent, application-platform, framework, test-runner, or optional-trait policy in skill bodies.

Permanent skills SHALL retain stage-specific operations, hard gates, verification authority, OpenSpec operation ownership, and zmem materiality in their owning skill. Cross-cutting advisory governance SHALL remain in independently configurable standard traits rather than being repeated across skill bodies. The permanent `zpp-configure-behavior` skill SHALL help an explicitly invoking agent inspect repository verification structure, initialize and revise only the declarative behavior mapping, validate it through ZPP core, and run its configured complete audit; config schema ownership, provider discovery, executable selection, filtering, plugin management, cache correctness, and process execution SHALL remain in ZPP core.

Each completed skill stage SHALL hand its result to the next owning workflow. When automatic progression or explicit end-to-end delegation applies, a satisfied checkpoint or ordinary stage transition SHALL continue without an approval-only pause.

The permanent codespace worktree-reconciliation skill SHALL consume recorded effective/source checkout and branch metadata only after explicit invocation. It SHALL NOT make codespace lifecycle operations merge work automatically or implicitly delete branches, worktrees, or released metadata.

ZPP SHALL establish managed ownership and compatibility through bundle metadata plus exact owned content rather than directory names. Passive trait `skill_lookup` metadata SHALL NOT execute a skill or grant authority.

#### Scenario: Use the permanent workflow bundle
- **WHEN** a user installs the workflow skills and resolves the standard advisory traits
- **THEN** all twelve skills project coherently, stage-specific enforcement remains skill-owned, and shared guidance and automatic handoffs remain advisory

#### Scenario: Configure repository behavior explicitly
- **WHEN** a user or agent explicitly invokes `zpp-configure-behavior`
- **THEN** the skill may author the declarative repository mapping through the public ZPP surface without becoming an execution provider or runtime authority

#### Scenario: Reconcile isolated codespace work explicitly
- **WHEN** a user explicitly invokes reconciliation for recorded codespace branches
- **THEN** the reconciliation skill uses their retained metadata without weakening lifecycle isolation

### Requirement: Complete global workflow installation
A global `workflow install` SHALL establish the complete ZPP workflow integration for every selected Pi, Codex, or Claude Code agent and SHALL compatibly upgrade the persistent default profile. Success SHALL leave each selected agent with the current managed ZPP workflow bundle, its current native ZPP lifecycle hooks, and the OpenSpec core operation skills emitted for that agent by the installed OpenSpec version in the agent's global skill location, while adding only standard-profile entries absent from the valid persistent default.

ZPP SHALL obtain OpenSpec-owned skill content from OpenSpec rather than packaging or reauthoring that content. Installation SHALL preflight every selected destination, generated skill set, and persistent default mutation before committing any selected-agent or profile change, preserve unrelated agent and authored profile content, reject unmanaged agent conflicts or malformed profile state without overwrite, and be idempotent against an already complete compatible installation.

ZPP SHALL generate the OpenSpec skills in an isolated platform-neutral project beneath the operating system's temporary directory, copy only the generated selected-agent skill projections to their global locations, and remove the temporary project after success or failure.

#### Scenario: Install a complete global workflow
- **WHEN** a user globally installs the workflow for one or more selected agents against compatible state
- **THEN** every selected agent receives the ZPP bundle, current native lifecycle hooks, and its OpenSpec-generated core operation skills while the persistent default receives only missing packaged entries as one complete installation outcome

#### Scenario: Preserve selected agents after a dependency conflict
- **WHEN** any selected hook, ZPP projection, generated OpenSpec skill set, OpenSpec skill destination, or persistent default preflight conflicts or is malformed
- **THEN** installation fails without changing any selected agent or profile surface and preserves unrelated content

#### Scenario: Repeat a complete global installation
- **WHEN** the selected agents and persistent default already have a complete compatible global workflow installation
- **THEN** installation succeeds without rewriting their managed, authored, or unrelated content

### Requirement: Workflow lifecycle isolation from authored profiles
Workflow lifecycle operations SHALL normally operate only on selected managed agent projections. As the sole exception, user-global workflow install and update SHALL compatibly add packaged standard trait files and trigger entries absent from a valid persistent `default` profile while preserving all existing same-name files, trigger values, configuration values, and custom traits. Repository-local workflow lifecycle operations and workflow removal SHALL NOT create, modify, rename, or remove any user profile or authored trait content.

#### Scenario: Upgrade the default during global maintenance
- **WHEN** a user installs or updates a user-global workflow projection against a valid persistent default
- **THEN** ZPP adds only missing packaged standard entries and otherwise preserves the authored profile

#### Scenario: Maintain skills without changing profiles
- **WHEN** a user installs or updates a repository-local workflow, declines removal, or confirms removal of selected workflow projections
- **THEN** only eligible managed agent projection state changes and every authored profile remains unchanged
