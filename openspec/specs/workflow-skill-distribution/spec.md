# workflow-skill-distribution Specification

## Purpose

Defines safe distribution and lifecycle management of ZPP's permanent workflow-skill bundle across supported agents' native global and repository-local skill scopes.

## Requirements

### Requirement: Permanent workflow bundle ownership
ZPP SHALL package the eleven permanent `zpp-*` workflow skills as one versioned owned bundle. Installed copies SHALL be projections of the packaged bundle, preserve every required skill resource, and SHALL NOT embed agent, application-platform, framework, test-runner, or optional-trait policy in skill bodies.

Permanent skills SHALL retain stage-specific operations, hard gates, verification authority, OpenSpec operation ownership, and zmem materiality in their owning skill. Cross-cutting advisory governance SHALL remain in independently configurable standard traits rather than being repeated across skill bodies.

Each completed skill stage SHALL hand its result to the next owning workflow. When automatic progression or explicit end-to-end delegation applies, a satisfied checkpoint or ordinary stage transition SHALL continue without an approval-only pause.

The permanent codespace worktree-reconciliation skill SHALL consume recorded effective/source checkout and branch metadata only after explicit invocation. It SHALL NOT make codespace lifecycle operations merge work automatically or implicitly delete branches, worktrees, or released metadata.

ZPP SHALL establish managed ownership and compatibility through bundle metadata plus exact owned content rather than directory names. Passive trait `skill_lookup` metadata SHALL NOT execute a skill or grant authority.

#### Scenario: Use the permanent workflow bundle
- **WHEN** a user installs the workflow skills and resolves the standard advisory traits
- **THEN** all eleven skills project coherently, stage-specific enforcement remains skill-owned, and shared guidance and automatic handoffs remain advisory

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
ZPP SHALL expose independent `workflow install`, `workflow update`, and `workflow remove` commands for Pi, Codex, and Claude Code. The lifecycle SHALL support user-global scope or an exact existing repository-local directory inside a Git worktree and SHALL NOT create or modify an authored `.zpp` layer. ZPP SHALL NOT expose the former generic `skill` command group.

Codex and Pi SHALL share their native `.agents/skills` projection, while Claude Code SHALL use its native `.claude/skills` projection. Agent-specific destination rules SHALL remain outside the workflow-skill bodies.

#### Scenario: Select lifecycle scope and agents
- **WHEN** a user invokes a workflow lifecycle command with a valid scope and supported agent selection
- **THEN** ZPP targets only the corresponding native projection or rejects the invocation before changing agent state

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
Workflow installation, update, and removal SHALL operate only on selected managed agent projections. These operations SHALL NOT create, modify, rename, or remove any user profile or authored trait content, including the persistent `default` profile.

#### Scenario: Maintain skills without changing profiles
- **WHEN** a user installs, updates, declines removal, or confirms removal of selected workflow projections
- **THEN** only eligible managed agent projection state changes and every authored profile remains unchanged

### Requirement: Stage-owned OpenSpec change disposition
Permanent workflow skills SHALL own the lifecycle operations appropriate to
their stages. Clarification SHALL establish the session-local related set.
Utility planning SHALL register its companion as disposable, and utility
maturity SHALL discard it and verify its absence before wiring. Specification
formation SHALL hand the product change to the owning OpenSpec finalizer and
then audit the related set.

A consumed internal anchor whose consumer condition is satisfied SHALL be
discarded. Genuinely unfinished related work MAY remain active only under an
identified owning stage. A consumed related change without an owner SHALL block
the workflow completion claim.

#### Scenario: Apply stage-owned terminal dispositions
- **WHEN** a mature workflow disposes its utility scaffolding and finalizes its product change
- **THEN** the owning skills verify those dispositions and reject completion if any consumed related change remains unowned

### Requirement: Authority-aware workflow reconciliation
Clarification SHALL compare relevant temporal zmem history with the current
canonical OpenSpec baseline before persisting accepted change material. The
proposal SHALL retain motivation, scope, capability inventory, impact, and
unresolved owner decisions. Every declared new or modified capability SHALL
have a corresponding OpenSpec delta at `specs/<capability>/spec.md`, and
clarification SHALL persist settled behavioral requirements into their owning
deltas instead of collapsing the complete contract into `proposal.md`.

Feature shaping SHALL consume the proposal and every declared delta spec. Once
Gherkin owns executable examples, shaping SHALL remove only duplicated examples
from the OpenSpec artifacts and SHALL preserve their stable intent,
constraints, invariants, and acceptance obligations. Specification formation
SHALL reconcile the existing deltas against mature green behavior before
promoting them into canonical OpenSpec.

ZPP SHALL leave abandoned or superseded chronology in zmem and SHALL NOT
require zmem dependency-graph semantics. Design and task artifacts SHALL follow
the selected OpenSpec schema and artifact instructions rather than a universal
ZPP one-file restriction.

#### Scenario: Clarify a multi-capability change
- **WHEN** clarification settles behavior for capabilities declared by an OpenSpec proposal
- **THEN** the overview remains in `proposal.md` and each capability contract is persisted in its own delta spec

#### Scenario: Reconcile a changed decision
- **WHEN** a change has canonical behavior, mutable planning artifacts, and temporally ordered zmem decisions
- **THEN** the workflow forms current authority from mature accepted behavior without treating historical directions as current truth

### Requirement: Explicit temporal-memory checkpoints
Every material workflow gate SHALL produce its required logical commit, but SHALL add zmem only when that commit contains a meaningful decision change, reversal, fallback, surprise, or lesson worthy of durable temporal recall. Verification, stage completion, or specification adoption alone SHALL NOT require or repeat a zmem annotation.

The bundled commit-message validators SHALL accept valid conventional commits with zero zmem annotations in normal mode and SHALL require at least one canonical annotation when memory-bearing validation is explicitly requested.

#### Scenario: Validate ordinary and memory-bearing commits
- **WHEN** the same valid unannotated conventional message is checked normally and as a memory-bearing checkpoint
- **THEN** normal validation succeeds and memory-bearing validation rejects the missing canonical zmem annotation

Executable public examples for every requirement are maintained in `features/workflow_skill_distribution.feature`.
