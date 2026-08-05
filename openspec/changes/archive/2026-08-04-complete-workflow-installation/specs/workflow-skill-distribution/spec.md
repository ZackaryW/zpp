## MODIFIED Requirements

### Requirement: Explicit skill lifecycle and scope
ZPP SHALL expose independent `workflow install`, `workflow update`, and `workflow remove` commands for Pi, Codex, and Claude Code. The lifecycle SHALL support user-global scope or an exact existing repository-local directory inside a Git worktree and SHALL NOT create or modify an authored `.zpp` layer. ZPP SHALL NOT expose the former generic `skill` command group.

Codex SHALL use `.agents/skills`. Pi SHALL use `.pi/skills` in repository-local scope and `.pi/agent/skills` in user-global scope. Claude Code SHALL use `.claude/skills`. Agent-specific destination rules SHALL remain outside the workflow-skill bodies.

#### Scenario: Select lifecycle scope and agents
- **WHEN** a user invokes a workflow lifecycle command with a valid scope and supported agent selection
- **THEN** ZPP targets only the corresponding native projection or rejects the invocation before changing agent state

#### Scenario: Keep Pi and Codex projections independent
- **WHEN** a workflow lifecycle operation selects Pi, Codex, or both
- **THEN** Pi's `.pi` projection and Codex's `.agents` projection are planned, owned, and maintained independently

## ADDED Requirements

### Requirement: Complete global workflow installation
A global `workflow install` SHALL establish the complete ZPP workflow integration for every selected Pi, Codex, or Claude Code agent. Success SHALL leave each selected agent with the current managed ZPP workflow bundle, its current native ZPP lifecycle hooks, and the OpenSpec core operation skills emitted for that agent by the installed OpenSpec version in the agent's global skill location.

ZPP SHALL obtain OpenSpec-owned skill content from OpenSpec rather than packaging or reauthoring that content. Installation SHALL preflight every selected destination and generated skill set before committing any selected-agent change, preserve unrelated agent content, reject unmanaged conflicts without overwrite, and be idempotent against an already complete compatible installation.

ZPP SHALL generate the OpenSpec skills in an isolated platform-neutral project beneath the operating system's temporary directory, copy only the generated selected-agent skill projections to their global locations, and remove the temporary project after success or failure.

#### Scenario: Install a complete global workflow
- **WHEN** a user globally installs the workflow for one or more selected agents against compatible state
- **THEN** every selected agent receives the ZPP bundle, current native lifecycle hooks, and its OpenSpec-generated core operation skills as one complete installation outcome

#### Scenario: Preserve selected agents after a dependency conflict
- **WHEN** any selected hook, ZPP projection, generated OpenSpec skill set, or OpenSpec skill destination conflicts or cannot be preflighted
- **THEN** installation fails without changing any selected agent surface and preserves unrelated content

#### Scenario: Repeat a complete global installation
- **WHEN** the selected agents already have a complete compatible global workflow installation
- **THEN** installation succeeds without rewriting their managed or unrelated content

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
