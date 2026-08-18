## MODIFIED Requirements

### Requirement: Agent-native automatic trait hooks
ZPP SHALL package one native trait-context hook for each supported Agent Router agent. Each hook SHALL invoke `zpp resolve --agent <agent> .` at the earliest native context-injection event, and that invocation SHALL establish the session for the repository so space-scoped sources resolve without an explicit `--space` argument or `OPENLEASE_SPACE` value. The hook SHALL inject only the successful command's prompt-ready complete trait bodies. The hook SHALL NOT declare an affected claim, evaluate lockability, acquire a permit, dispatch workflow stages, or grant mutation, transition, verification, or completion authority.

#### Scenario: Inject traits for a supported agent session
- **WHEN** an installed Codex, Claude Code, Pi, or Kimi integration begins its earliest supported context-injection event in a repository
- **THEN** its native hook resolves traits with that agent identity, establishes the session, and contributes the successful prompt-ready body output as environment policy

#### Scenario: Resolve space-scoped sources without explicit selection
- **WHEN** a native hook resolves traits in a repository and supplies no `--space` argument and no `OPENLEASE_SPACE` value
- **THEN** the established session supplies the selected space and its space-scoped sources contribute to resolution

#### Scenario: Keep permit authority out of the hook
- **WHEN** a native hook establishes the session for a repository
- **THEN** it declares no affected claim and acquires no permit, leaving every modification gated by an explicit claim and go-ahead

#### Scenario: Keep workflow authority out of the hook
- **WHEN** an injected trait body describes a workflow action or claims completion
- **THEN** the hook contributes only advisory context and does not execute or authorize that action
