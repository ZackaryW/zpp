## ADDED Requirements

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

## MODIFIED Requirements

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
