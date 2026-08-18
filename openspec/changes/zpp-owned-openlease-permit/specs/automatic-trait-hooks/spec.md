## MODIFIED Requirements

### Requirement: Agent-native automatic trait hooks
ZPP SHALL package one native trait-context hook for each supported Agent Router agent. Each hook SHALL invoke `zpp resolve --agent <agent> .` at the earliest native context-injection event, and that invocation SHALL establish the session for the repository so space-scoped sources resolve without an explicit `--space` argument or `OPENLEASE_SPACE` value. The hook SHALL inject only the successful command's prompt-ready complete trait bodies. The hook SHALL NOT declare an affected claim, evaluate lockability, acquire a permit, dispatch workflow stages, or grant mutation, transition, verification, or completion authority.

#### Scenario: Inject traits for a supported agent session
- **WHEN** an installed Codex, Claude Code, Pi, or Kimi integration begins its earliest supported context-injection event in a repository
- **THEN** its native hook resolves traits with that agent identity, establishes the session, and contributes the successful prompt-ready body output as environment policy

#### Scenario: BDD target — Establish the session from a native hook resolution
- **WHEN** executable behavior is covered by `features/automatic_trait_hooks/automatic_trait_hooks.feature::Establish the session from a native hook resolution`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Resolve space-scoped sources without explicit selection
- **WHEN** executable behavior is covered by `features/automatic_trait_hooks/automatic_trait_hooks.feature::Resolve space-scoped sources without explicit selection`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Keep permit authority out of the hook
- **WHEN** executable behavior is covered by `features/automatic_trait_hooks/automatic_trait_hooks.feature::Keep permit authority out of the hook`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: Keep workflow authority out of the hook
- **WHEN** an injected trait body describes a workflow action or claims completion
- **THEN** the hook contributes only advisory context and does not execute or authorize that action
