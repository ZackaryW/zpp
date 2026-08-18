# Automatic Trait Hooks Specification

## Purpose

Define agent-native automatic trait resolution and context injection without transferring workflow authority to hooks.

## Requirements

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

### Requirement: Native hook forms
ZPP SHALL provide Agent Router `Hook` assets using JSON session-start hooks for Codex and Claude Code, a TOML session-start hook for Kimi, and a Pi TypeScript `before_agent_start` extension that appends successful resolver output to the system prompt. ZPP SHALL delegate native destination adaptation and writes to Agent Router.

#### Scenario: Inspect packaged hooks
- **WHEN** ZPP's hook artifacts are inspected for all supported agents
- **THEN** each artifact uses that agent's required native form and names the matching `--agent` value

### Requirement: Hook failure isolation
A hook SHALL make resolver failure visible according to the native agent hook contract and SHALL inject no stale or partial trait body output from that failed invocation. ZPP SHALL NOT maintain a hidden trait-output cache for hook fallback.

#### Scenario: Resolution fails during session injection
- **WHEN** the hook's resolver invocation fails before producing a successful result
- **THEN** the failure remains observable and no body from that invocation or an earlier invocation is injected as successful context

### Requirement: Agent Router-owned hook lifecycle
Root initialization and grouped workflow lifecycle operations SHALL project and remove the selected agent's packaged hook through Agent Router together with the consolidated workflow skill. Install and update SHALL use Agent Router's hook installation contract, removal SHALL use its hook uninstallation contract, and ZPP SHALL NOT write hook destinations directly.

Confirmed product reset SHALL separately inspect every supported agent's packaged `zpp-session` hook in user scope and remove each present ownership-safe hook through Agent Router only after complete reset preflight succeeds. Reset SHALL NOT broaden ordinary grouped workflow removal, target project-scope hooks, or directly mutate a native hook destination.

#### Scenario: Install a complete workflow integration
- **WHEN** a user installs the ZPP workflow integration for a supported agent and scope
- **THEN** Agent Router projects both the consolidated skill and that agent's native hook

#### Scenario: Remove a complete workflow integration
- **WHEN** a user removes an intact Agent Router-owned ZPP workflow integration for a supported agent and scope
- **THEN** Agent Router removes both the consolidated skill and native hook for that scope

#### Scenario: Reset every user-scope hook safely
- **WHEN** confirmed reset preflight proves each supported agent's user-scope ZPP hook absent or ownership-safe removable
- **THEN** reset removes every present selected hook through Agent Router without inspecting or changing project-scope hooks

#### Scenario: Preserve hooks on reset conflict
- **WHEN** any supported agent's selected user-scope hook is modified, unmanaged, ambiguous, conflicting, or cannot be inspected
- **THEN** complete reset aborts before removing any hook or changing OpenLease state
