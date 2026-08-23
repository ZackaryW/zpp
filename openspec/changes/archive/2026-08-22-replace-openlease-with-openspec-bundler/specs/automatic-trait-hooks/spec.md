## MODIFIED Requirements

### Requirement: Agent-native automatic trait hooks
ZPP SHALL package one native trait-context hook named `zpp-traits` for each supported Agent Router agent. Each hook SHALL invoke `zpp resolve --agent <agent> .` at the earliest native context-injection event, inject only the successful command's prompt-ready complete trait bodies, and create no session, claim, lease, or other coordination state. The hook SHALL NOT dispatch workflow stages or grant mutation, transition, verification, or completion authority.

#### Scenario: Inject traits without coordination state
- **WHEN** an installed supported agent begins its earliest context-injection event in a repository
- **THEN** `zpp-traits` resolves and injects the successful trait bodies without creating session or lease state

#### Scenario: Keep workflow authority out of the hook
- **WHEN** an injected trait body describes a workflow action or claims completion
- **THEN** the hook contributes only advisory context and does not execute or authorize that action

### Requirement: Agent Router-owned hook lifecycle
Root initialization and grouped workflow lifecycle operations SHALL project and remove the selected agent's packaged `zpp-traits` hook through Agent Router together with the consolidated workflow skill. Install and update SHALL use Agent Router's hook installation contract, removal SHALL use its hook uninstallation contract, and ZPP SHALL NOT write hook destinations directly. Confirmed reset SHALL inspect and remove only the new hook identity and SHALL NOT search for, adopt, or remove the former `zpp-session` identity as a compatibility operation.

#### Scenario: Install a complete workflow integration
- **WHEN** a user installs the ZPP workflow integration for a supported agent and scope
- **THEN** Agent Router projects both the consolidated skill and that agent's `zpp-traits` hook

#### Scenario: Preserve hooks on reset conflict
- **WHEN** any selected `zpp-traits` hook is modified, unmanaged, ambiguous, conflicting, or cannot be inspected
- **THEN** complete reset aborts before removing any hook or changing Bundler state
