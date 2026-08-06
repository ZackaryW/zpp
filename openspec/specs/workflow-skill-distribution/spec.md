# workflow-skill-distribution Specification

## Purpose

Defines safe distribution and lifecycle management of ZPP's permanent workflow-skill bundle across supported agents' native global and repository-local skill scopes.

## Requirements

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

### Requirement: Complete zmem teaching
ZPP SHALL teach the complete supported zmem read surface through a permanent `zpp-use-zmem` skill and SHALL connect it coherently to the existing `zpp-commit-zmem` material-change commit skill. The executable-guarded `use-zmem` trait SHALL look up both skills. The guidance SHALL cover temporal recall, search, detail inspection, relationship traversal, output interpretation, and verification of historical evidence against current authority without treating recall as a blocking gate.

#### Scenario: Consult ZPP guidance for zmem
- **WHEN** an agent needs to learn or use zmem beyond commit annotation
- **THEN** the installed ZPP guidance exposes the relevant supported operation and explains how temporal evidence relates to current OpenSpec and code authority

### Requirement: Ponytail-grounded lean audit
ZPP SHALL distribute a read-only `zpp-lean-audit` skill substantially and explicitly grounded in Dietrich Gebert's upstream Ponytail project at `https://github.com/DietrichGebert/ponytail`, including its ladder, audit taxonomy, ranked output, and safety boundaries with appropriate attribution. The skill SHALL distinguish Ponytail's installed-dependency rung from ZPP's later utility-discovery extension for mature third-party packages, and SHALL evaluate external dependencies by maturity, integration cost, and proportional required surface rather than rejecting or adopting them solely because they are external.

#### Scenario: Audit excessive complexity
- **WHEN** a user requests a lean audit of an explicit target
- **THEN** the skill ranks justified delete, standard-library, native-platform, YAGNI, and shrink findings without applying fixes or simplifying away validation, data-loss protection, security, accessibility, or explicit requirements

### Requirement: Skill-authoring reference guidance
ZPP SHALL distribute a permanent `zpp-author-skill` skill containing `references/context-continuity.md` and `references/explicit-control-flow.md`. The references SHALL guide ZPP skill construction and review without activating as runtime traits or claiming authority over system, agent, user, or canonical OpenSpec instructions.

#### Scenario: Create or revise a ZPP skill
- **WHEN** a maintainer consults the packaged skill-authoring references
- **THEN** the guidance explains how to externalize durable state and define stop, pause, escalation, blocked-tool, and stage-transition behavior without injecting those directions into unrelated runtime work

### Requirement: Explicit skill lifecycle and scope
ZPP SHALL expose independent `workflow install`, `workflow update`, and `workflow remove` commands for Pi, Codex, and Claude Code. Each workflow lifecycle command SHALL select user-global scope when no scope option is supplied and SHALL select repository-local scope only when the user supplies `--local`. The public workflow lifecycle scope selector SHALL be `--local` rather than `--global`.

Repository-local scope SHALL target the current directory when no positional target is supplied or an exact existing directory inside a Git worktree when a target is supplied, and SHALL NOT create or modify an authored `.zpp` layer. A positional target without `--local` SHALL be rejected before changing managed or agent state. `--force` and `--with-openspec` SHALL be accepted only with `--local` and SHALL be rejected in global scope before changing managed or agent state. ZPP SHALL NOT accept `--global` as a workflow lifecycle option and SHALL NOT expose the former generic `skill` command group.

Codex SHALL use `.agents/skills` in repository-local scope and `.codex/skills` beneath the platform-native user home in user-global scope. Pi SHALL use `.pi/skills` in repository-local scope and `.pi/agent/skills` in user-global scope. Claude Code SHALL use `.claude/skills` in both scopes. Agent-specific destination rules SHALL remain outside the workflow-skill bodies. ZPP workflow and generated OpenSpec ownership manifests SHALL coexist independently when they share an agent's skill root.

#### Scenario: Default lifecycle scope to global
- **WHEN** a user invokes `workflow install`, `workflow update`, or `workflow remove` without `--local`
- **THEN** ZPP targets only the corresponding user-global native projection or rejects the invocation before changing agent state

#### Scenario: Select repository-local lifecycle scope explicitly
- **WHEN** a user invokes a workflow lifecycle command with `--local` and a valid supported agent selection
- **THEN** ZPP targets only the corresponding repository-local native projection at the supplied target or current directory when omitted, or rejects the invocation before changing agent state

#### Scenario: Reject local syntax without the local selector
- **WHEN** a user supplies a positional repository target without `--local`, supplies the removed `--global` option, or supplies a local-only install control in global scope
- **THEN** ZPP rejects the invocation before changing managed or agent state

#### Scenario: Keep Pi and Codex projections independent
- **WHEN** a workflow lifecycle operation selects Pi, Codex, or both
- **THEN** Pi's `.pi` projection and Codex's scope-specific projection are planned, owned, and maintained independently

#### Scenario: Select Codex destinations by scope
- **WHEN** a user installs or maintains Codex workflow skills globally and repository-locally
- **THEN** the global bundle uses the active user's `.codex/skills` while the local bundle uses `.agents/skills`, with unrelated and independently managed skills preserved in each root on macOS, Windows, and Linux

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

### Requirement: Complete selected-agent initialization
Initialization with one or more explicitly or interactively selected agents SHALL establish the complete current user-global workflow integration for exactly those agents. Success SHALL leave each selected agent with the current managed ZPP workflow bundle, its current native ZPP lifecycle hooks, and the OpenSpec core operation skills emitted for that agent by the installed OpenSpec version in the agent's global skill location.

Initialization SHALL use the established complete global installation ownership and compatibility rules: it SHALL install absent projections, replace intact outdated managed ZPP projections, regenerate outdated managed OpenSpec projections according to the detected-version contract, preserve compatible projections without rewriting them, and reject malformed, modified, unsafe, or unmanaged conflicting state without overwrite. It SHALL obtain OpenSpec-owned skill content through isolated generation and SHALL preserve unrelated agent content.

Initialization SHALL preflight every selected agent's included hook, workflow, and OpenSpec destination before changing any selected agent surface, and SHALL apply the complete selected-agent integration atomically. Neutral ZPP user-state initialization MAY complete before a later selected-agent conflict is reported, but a failed selected-agent setup SHALL leave every selected agent surface unchanged. An existing valid user-owned default profile SHALL remain byte-for-byte unchanged during initialization.

Initialization without a selected agent, an empty interactive selection, and a cancelled interactive selection SHALL NOT create or change workflow or OpenSpec skill projections. Repository-local projections and unselected agents SHALL remain unchanged in every initialization outcome.

#### Scenario: Initialize a selected agent with missing workflow skills
- **WHEN** a user runs `zpp init --agent codex` while Codex lacks the managed ZPP workflow bundle but has compatible global OpenSpec skills
- **THEN** Codex receives the current ZPP workflow bundle and native hooks under its global locations while its compatible OpenSpec skills, unrelated content, and repository-local projections remain unchanged

#### Scenario: Complete every selected integration atomically
- **WHEN** initialization selects multiple agents whose complete global integrations can all be established safely
- **THEN** every selected agent receives its current ZPP bundle, native hooks, and OpenSpec core skills as one selected-agent setup outcome

#### Scenario: Reject a selected integration conflict without partial agent setup
- **WHEN** any selected hook, ZPP projection, generated OpenSpec skill set, or OpenSpec destination conflicts or cannot be preflighted
- **THEN** initialization may retain successfully created neutral ZPP user state but changes no selected agent surface and preserves unrelated content

#### Scenario: Refresh an intact outdated selected integration
- **WHEN** initialization selects an agent with intact outdated managed ZPP or OpenSpec projections
- **THEN** it establishes the current complete selected-agent integration through the existing managed replacement and version-aware generation rules

#### Scenario: Repeat complete selected-agent initialization
- **WHEN** a selected agent already has a complete compatible global workflow integration
- **THEN** initialization succeeds without rewriting its managed, generated, or unrelated agent content or the existing valid default profile

#### Scenario: Initialize without selecting an agent
- **WHEN** initialization receives no selected agent through a noninteractive invocation, empty submission, or cancellation
- **THEN** it creates or changes no global or repository-local workflow or OpenSpec skill projection

### Requirement: Optional local OpenSpec skill bootstrap
Repository-local `workflow install` SHALL preserve its existing ZPP-only projection behavior unless the user explicitly opts into OpenSpec skill bootstrap. With that opt-in, ZPP SHALL use the same isolated generation boundary and project the selected agents' generated OpenSpec core skills into their corresponding repository-local skill locations.

#### Scenario: Install locally without OpenSpec opt-in
- **WHEN** a user installs a repository-local workflow without explicitly requesting OpenSpec skill bootstrap
- **THEN** ZPP installs only its managed local workflow bundle and does not create or change local OpenSpec skill projections

#### Scenario: Opt into complete local workflow skills
- **WHEN** a user explicitly requests OpenSpec skill bootstrap during repository-local workflow installation
- **THEN** each selected agent receives both the managed ZPP workflow bundle and its OpenSpec-generated core operation skills in the selected repository

### Requirement: Version-aware OpenSpec skill maintenance
ZPP SHALL record the detected OpenSpec version used to generate each managed OpenSpec skill projection. When version detection is unavailable but generation succeeds, ZPP SHALL record `null`. Workflow update SHALL regenerate the selected OpenSpec skill projection only when the currently detected version differs from the recorded value; an unchanged value, including `null` compared with `null`, SHALL preserve the existing projection without rewriting it.

Workflow removal SHALL leave shared OpenSpec skill projections and independently usable native hook integrations installed and SHALL continue to remove only metadata-owned ZPP workflow paths from the selected scope.

#### Scenario: Preserve skills for an unchanged OpenSpec version
- **WHEN** workflow update detects the same OpenSpec version value recorded for the selected generated projection
- **THEN** the existing OpenSpec skills remain byte-for-byte unchanged

#### Scenario: Regenerate skills after an OpenSpec version change
- **WHEN** workflow update detects an OpenSpec version value different from the selected projection's recorded value
- **THEN** ZPP replaces the managed generated OpenSpec skill set with the newly generated selected-agent core skills and records the new value

#### Scenario: Preserve shared OpenSpec skills during removal
- **WHEN** a user removes the selected ZPP workflow bundle
- **THEN** the selected ZPP-owned workflow paths are removed and the generated OpenSpec skill projection remains installed

### Requirement: Agent selection for skill lifecycle
Repeated explicit agent selections SHALL bypass prompting. Without explicit selections, an interactive workflow lifecycle invocation SHALL offer Pi, Codex, and Claude Code as a zero-or-more selector; empty submission SHALL succeed without changes and cancellation SHALL make no changes. A noninteractive workflow lifecycle invocation without explicit agents SHALL be a usage error.

#### Scenario: Resolve lifecycle agent selection
- **WHEN** a workflow lifecycle command obtains explicit, interactive-empty, cancelled, or missing-noninteractive selection input
- **THEN** it follows the established selection outcome without inferring an agent

### Requirement: Compatible installation and coexistence
Installation SHALL preflight the complete bundle and every selected destination before mutation, preserve unrelated content, and reject unmanaged or conflicting destinations without overwrite. Repeating installation against a compatible selected projection SHALL be idempotent.

Local installation SHALL reuse a compatible managed global projection by default. An absent or outdated global projection SHALL NOT suppress current local installation. `--force` SHALL bypass only compatible-global deduplication and SHALL NOT authorize conflict replacement. Managed global and local projections MAY coexist; ZPP SHALL report coexistence and differing versions without asserting scope precedence.

#### Scenario: Plan installation from all selected state
- **WHEN** installation evaluates selected destinations together with corresponding global compatibility
- **THEN** it either applies the complete safe plan or leaves every selected destination unchanged

### Requirement: Managed update and removal
Update SHALL operate only on the explicitly selected managed scope, make compatible projections no-ops, replace outdated managed projections with the packaged bundle, and leave every unselected global or local scope unchanged.

A structurally valid historical manifest SHALL remain ownership evidence when its declared bundle version or complete owned file set differs from the current packaged bundle. ZPP SHALL validate the historical projection against exactly the paths and digests declared by that manifest, classify the intact projection as outdated, remove only those declared owned paths during replacement, and install the complete current bundle and manifest atomically.

Removal SHALL require confirmation unless `--yes` or `-y` is supplied and SHALL remove only metadata-owned ZPP paths from the selected managed projection. Update and removal SHALL reject absent projections, malformed manifests, unsafe manifest paths, content that differs from its manifest, conflicting paths, or user-owned selected state without partial mutation. Diagnostics SHALL distinguish absent selected state from malformed, conflicting, or user-owned state.

#### Scenario: Maintain one selected managed scope
- **WHEN** a user updates or confirms removal for selected managed projections
- **THEN** only their owned state changes and unrelated or unselected state remains unchanged

#### Scenario: Update an intact historical managed bundle
- **WHEN** a selected projection exactly matches a structurally valid manifest for an earlier workflow bundle
- **THEN** ZPP replaces only its declared owned paths with the current complete bundle and preserves unrelated content

#### Scenario: Reject an absent selected projection clearly
- **WHEN** a user requests update or removal in a scope with no managed projection
- **THEN** ZPP rejects the request as not installed in that scope without describing it as unmanaged content

### Requirement: Workflow lifecycle isolation from authored profiles
Workflow lifecycle operations SHALL normally operate only on selected managed agent projections. As the sole exception, user-global workflow install and update SHALL compatibly add packaged standard trait files and trigger entries absent from a valid persistent `default` profile while preserving all existing same-name files, trigger values, configuration values, and custom traits. Repository-local workflow lifecycle operations and workflow removal SHALL NOT create, modify, rename, or remove any user profile or authored trait content.

#### Scenario: Upgrade the default during global maintenance
- **WHEN** a user installs or updates a user-global workflow projection against a valid persistent default
- **THEN** ZPP adds only missing packaged standard entries and otherwise preserves the authored profile

#### Scenario: Maintain skills without changing profiles
- **WHEN** a user installs or updates a repository-local workflow, declines removal, or confirms removal of selected workflow projections
- **THEN** only eligible managed agent projection state changes and every authored profile remains unchanged

### Requirement: Automatic maintenance of installed global workflows
Top-level `zpp update` SHALL inspect the supported Pi, Codex, and Claude Code global workflow locations without requiring agent selection. Every compatible or outdated managed ZPP workflow bundle it discovers SHALL be maintained as one complete integration with the current packaged ZPP bundle, current native lifecycle hooks, and OpenSpec core operation skills generated for that agent by the installed OpenSpec version. An absent ZPP workflow bundle SHALL remain absent and SHALL NOT cause its agent's OpenSpec skill projection to be installed merely because another owned surface is present.

For a discovered managed workflow bundle, global update SHALL repair an absent managed OpenSpec projection, preserve a verified projection when its recorded OpenSpec version matches the detected value, and regenerate it only when the detected value differs, including `null` comparison. It SHALL obtain OpenSpec-owned content through isolated platform-neutral OpenSpec generation and SHALL preserve unrelated agent content.

Global update SHALL preflight every discovered workflow, generated OpenSpec skill set, destination, hook, and persistent-default mutation before changing any included surface. A malformed ownership manifest, modified managed content, unsafe path, unmanaged collision, generation failure, or profile conflict SHALL reject the complete update without partial changes. Repository-local projections SHALL remain untouched.

#### Scenario: Refresh all installed managed global workflows
- **WHEN** global update discovers managed global workflow bundles for any combination of supported agents
- **THEN** it updates every discovered bundle and its complete hook and OpenSpec integration while leaving agents without a bundle uninstalled

#### Scenario: Preserve matching OpenSpec projections
- **WHEN** a discovered workflow's verified OpenSpec projection records the currently detected version value
- **THEN** global update preserves that projection byte-for-byte

#### Scenario: Regenerate changed OpenSpec projections
- **WHEN** a discovered workflow's OpenSpec projection is absent or records a different version value
- **THEN** global update installs or regenerates only that managed generated projection from the current isolated OpenSpec output

#### Scenario: Reject a discovered workflow conflict atomically
- **WHEN** any discovered workflow integration or the persistent default cannot be safely preflighted
- **THEN** global update identifies the conflict and changes none of the discovered global or local surfaces

#### Scenario: Keep local workflow state isolated
- **WHEN** compatible or conflicting repository-local workflow projections exist during global update
- **THEN** global update does not inspect them as update targets and leaves them unchanged

#### Scenario: Repeat global update idempotently
- **WHEN** every discovered global surface and the persistent default already match the current compatible state
- **THEN** global update succeeds without rewriting managed, authored, generated, or unrelated content

### Requirement: Stage-owned OpenSpec change disposition
Permanent workflow skills SHALL own the lifecycle operations appropriate to
their stages. Clarification SHALL establish the session-local related set.
Utility planning SHALL register its companion as disposable, and utility
maturity SHALL discard it and verify its absence before wiring. Specification
formation SHALL hand the product change to the owning OpenSpec finalizer, hand
the exact finalized archive to `zpp-commit-zmem` for a distinct repository-history
checkpoint, and then audit the related set. Active product-change artifacts
SHALL remain uncommitted mutable working state before finalization. A finalized
product archive SHALL be tracked as durable history, while unrelated active
changes and disposable utility plans SHALL be excluded from its checkpoint.

A consumed internal anchor whose consumer condition is satisfied SHALL be
discarded. Genuinely unfinished related work MAY remain active only under an
identified owning stage. A consumed related change without an owner SHALL block
the workflow completion claim.

#### Scenario: Apply stage-owned terminal dispositions
- **WHEN** a mature workflow disposes its utility scaffolding and finalizes its product change
- **THEN** the owning skills verify those dispositions and reject completion if any consumed related change remains unowned

#### Scenario: Checkpoint a finalized product archive
- **WHEN** the owning OpenSpec finalizer returns the exact archive path after canonical specification formation
- **THEN** the workflow commits that archive as durable repository history without sweeping unrelated active changes or requiring zmem merely for finalization

### Requirement: Authority-aware workflow reconciliation
Before product-change bootstrapping, clarification SHALL classify every requested outcome by observable ownership as repository-environment/tooling work, shipped source/product behavior, or a mixed request. Environmental-only work SHALL remain outside product capability deltas, Gherkin, and canonical product specifications and SHALL use its native implementation and verification surface. For a mixed request, clarification SHALL split the work so only shipped behavior enters the product change. A path or filename alone SHALL NOT override the observable ownership classification, and a genuinely ambiguous classification SHALL be resolved before product OpenSpec creation or selection.

For shipped behavior, clarification SHALL compare relevant temporal zmem history with the current canonical OpenSpec baseline before persisting accepted change material. Clarification SHALL discover relevant temporal history only through bounded `zmem recall` filters, SHALL NOT invoke `zmem search`, and MAY inspect an already identified relevant record with `zmem show`. When bounded recall yields no relevant history, clarification SHALL continue from canonical OpenSpec and current repository evidence without treating the missing history as a gate. The proposal SHALL retain motivation, scope, capability inventory, impact, and unresolved owner decisions. Every declared new or modified capability SHALL have a corresponding OpenSpec delta at `specs/<capability>/spec.md`, and clarification SHALL persist settled behavioral requirements into their owning deltas instead of collapsing the complete contract into `proposal.md`.

Feature shaping SHALL consume the proposal and every declared delta spec. In a monorepo, shaping SHALL identify each justifiably affected subproject from established repository boundaries and SHALL place executable behavior in each affected subproject's native feature surface. It SHALL NOT require one root-level feature file, framework, runner, or uniform project structure, SHALL NOT treat unaffected subprojects as part of the feature contract, and SHALL create a cross-subproject scenario only when the accepted public behavior itself crosses those boundaries. Once Gherkin owns executable examples, shaping SHALL remove only duplicated examples from the OpenSpec artifacts and SHALL preserve their stable intent, constraints, invariants, and acceptance obligations. Specification formation SHALL reconcile the existing deltas against mature green behavior before promoting them into canonical OpenSpec.

ZPP SHALL leave abandoned or superseded chronology in zmem and SHALL NOT require zmem dependency-graph semantics. Design and task artifacts SHALL follow the selected OpenSpec schema and artifact instructions rather than a universal ZPP one-file restriction.

#### Scenario: Classify work before product bootstrapping
- **WHEN** a request contains environmental tooling, shipped source behavior, or both
- **THEN** clarification classifies and separates those outcomes before product OpenSpec bootstrapping so environmental work does not become a product capability or BDD contract

#### Scenario: Clarify a multi-capability change
- **WHEN** clarification settles behavior for capabilities declared by an OpenSpec proposal
- **THEN** the overview remains in `proposal.md` and each capability contract is persisted in its own delta spec

#### Scenario: Shape justified monorepo feature surfaces
- **WHEN** an accepted shipped behavior change affects one or more established subprojects in a monorepo
- **THEN** feature shaping creates executable behavior only in each justifiably affected native feature surface without requiring a single repository-wide project shape

#### Scenario: Reconcile a changed decision
- **WHEN** a change has canonical behavior, mutable planning artifacts, and temporally ordered zmem decisions
- **THEN** the workflow forms current authority from mature accepted behavior without treating historical directions as current truth

#### Scenario: Continue without broad temporal search
- **WHEN** clarification investigates temporal history for a shipped behavior change
- **THEN** it uses bounded recall without invoking `zmem search` and continues from current authority when no relevant record is recalled

### Requirement: Explicit temporal-memory checkpoints
Every material workflow gate SHALL produce its required logical commit, including a distinct checkpoint for an exact finalized product archive, but SHALL add zmem only when that commit contains a meaningful decision change, reversal, fallback, surprise, or lesson worthy of durable temporal recall. Verification, stage completion, specification adoption, or archiving alone SHALL NOT require or repeat a zmem annotation.

The bundled commit-message validators SHALL accept valid conventional commits with zero zmem annotations in normal mode and SHALL require at least one canonical annotation when memory-bearing validation is explicitly requested.

#### Scenario: Validate ordinary and memory-bearing commits
- **WHEN** the same valid unannotated conventional message is checked normally and as a memory-bearing checkpoint
- **THEN** normal validation succeeds and memory-bearing validation rejects the missing canonical zmem annotation

Executable public examples for every requirement are maintained in `features/workflow_skill_distribution.feature`.
