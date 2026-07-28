## ADDED Requirements

### Requirement: Evidence-first learn-zpp skill
zpp SHALL ship an authoritative skill at `skills/learn-zpp/` whose trigger covers explaining, diagnosing, configuring, integrating, or changing zpp, including uncertainty about supporting tools when that uncertainty affects a zpp decision. The skill SHALL require agents to ground claims in target-specific resolver output, live CLI help, governing OpenSpec requirements and current code when applicable, and authoritative upstream documentation for external-tool semantics. It SHALL treat remembered behavior and examples from other repositories as leads rather than evidence.

#### Scenario: Resolver behavior is diagnosed
- **WHEN** an agent investigates why a nested project receives an unexpected stack
- **THEN** `learn-zpp` directs it to resolve the concrete target with both `zpp resolve --json` and `zpp config resolve --sources --json` before forming a conclusion

#### Scenario: External Git claim affects the design
- **WHEN** an agent's proposed zpp distribution design depends on a Git submodule or subtree constraint it has not verified
- **THEN** `learn-zpp` requires current authoritative Git documentation or live command evidence before accepting or rejecting the design

#### Scenario: Another repository's config is not evidence
- **WHEN** an agent recommends configuration for one repository
- **THEN** it uses that repository's resolver output rather than copying a template or another repository's `zpp.toml`

### Requirement: Learn-zpp remains diagnostic and routes mutations
`learn-zpp` SHALL remain a knowledge-and-diagnostic workflow. It SHALL NOT bootstrap tools, author configuration, provision isolation, implement resolver changes, or replace OpenSpec workflows. When the investigation calls for mutation, it SHALL identify and hand off to the appropriate existing workflow or implementation skill with the collected evidence.

#### Scenario: Missing toolchain needs remediation
- **WHEN** diagnosis shows that zpp or a governed dependency is missing
- **THEN** the skill routes remediation to the bootstrap workflow rather than installing it itself

#### Scenario: Resolver contract must change
- **WHEN** current specs and code cannot satisfy the requested behavior
- **THEN** the skill routes the work into an OpenSpec change instead of editing production code

### Requirement: Standard validated skill structure
The authoritative `skills/learn-zpp/` directory SHALL contain a valid `SKILL.md` with only `name` and `description` frontmatter, matching `agents/openai.yaml`, and only the one-level references or scripts required by its workflow. Validation SHALL use the standard skill validator, and representative forward tests SHALL demonstrate that an agent corrects plausible zpp misconceptions without being given the intended answer.

#### Scenario: Skill metadata validates
- **WHEN** the standard skill validator runs on `skills/learn-zpp`
- **THEN** its name, frontmatter, directory shape, and agent metadata pass

#### Scenario: Forward test begins from a misconception
- **WHEN** a fresh agent is asked a realistic zpp question containing a plausible but incorrect resolver or Git assumption
- **THEN** it follows the evidence workflow and either corrects the assumption or reports bounded uncertainty

### Requirement: Automated subtree-split publication
The `skills/learn-zpp/` directory on zpp's main branch SHALL be the only authored source of the skill. After a validated change to that directory reaches `main`, automation SHALL update a dedicated `dist/learn-zpp` branch whose repository root is exactly the skill contents. The split branch SHALL be suitable for mounting as a submodule at another repository's `skills/learn-zpp`, and consumers SHALL remain pinned to explicit distribution commits rather than following updates implicitly.

#### Scenario: Distribution branch has skill at root
- **WHEN** the split branch is checked out
- **THEN** `SKILL.md`, `agents/openai.yaml`, and declared references appear at the branch root rather than beneath `skills/learn-zpp`

#### Scenario: Invalid skill is not published
- **WHEN** skill validation fails on a main-branch candidate
- **THEN** automation does not advance `dist/learn-zpp`

#### Scenario: Downstream pins an exact release
- **WHEN** `dist/learn-zpp` advances after a skill update
- **THEN** an existing downstream gitlink remains at its recorded commit until that repository deliberately updates it
