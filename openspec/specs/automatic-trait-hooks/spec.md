# Automatic Trait Hooks Specification

## Purpose

Define agent-native automatic trait resolution and context injection without transferring workflow authority to hooks.

## Requirements

### Requirement: Agent-native automatic trait hooks
ZPP SHALL package one native trait-context hook named `zpp-traits` for each supported Agent Router agent. Each hook SHALL invoke `zpp resolve --agent <agent> .` at the earliest native context-injection event, inject only the successful command's prompt-ready complete trait bodies, and create no session, claim, lease, or other coordination state. The hook SHALL NOT dispatch workflow stages or grant mutation, transition, verification, or completion authority.

#### Scenario: Inject traits without coordination state
- **WHEN** an installed supported agent begins its earliest context-injection event in a repository
- **THEN** `zpp-traits` resolves and injects the successful trait bodies without creating session or lease state

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
Root initialization and grouped workflow lifecycle operations SHALL project and remove the selected agent's complete deterministic packaged workflow skill family and packaged `zpp-traits` hook through Agent Router. Install and update SHALL use Agent Router's skill and hook installation contracts, removal SHALL use its skill and hook uninstallation contracts, and ZPP SHALL NOT write either native destination directly. Confirmed reset SHALL inspect and remove only the new hook identity and SHALL NOT search for, adopt, or remove the former `zpp-session` identity as a compatibility operation.

Grouped `zpp workflow update` SHALL invoke shared current-plus-obsolete reconciliation in exactly the selected user or project scope. Project-scope update SHALL carry the exact project root through inspection, projection, verification, and owned-obsolete retirement without changing user scope. Grouped `zpp workflow install` SHALL preflight every current and obsolete destination in the selected scope, refuse any existing, unmanaged, or conflicting identity before projecting anything, preserve every existing destination, report the exact conflict, and direct an owned installation to update.

#### Scenario: Conformance trace for complete workflow-family installation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Install the complete workflow family and trait hook together"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Install the complete workflow family and trait hook together`

#### Scenario: Conformance trace for complete workflow-family removal
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Remove the complete workflow family and trait hook together"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Remove the complete workflow family and trait hook together`

#### Scenario: Conformance trace for project-scope legacy migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Update an owned old-only project workflow in place"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Update an owned old-only project workflow in place`

#### Scenario: Conformance trace for conflict-safe workflow installation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Refuse a conflicting workflow installation before mutation"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Refuse a conflicting workflow installation before mutation`

#### Scenario: Preserve hooks on reset conflict
- **WHEN** any selected `zpp-traits` hook is modified, unmanaged, ambiguous, conflicting, or cannot be inspected
- **THEN** complete reset aborts before removing any hook or changing Bundler state
