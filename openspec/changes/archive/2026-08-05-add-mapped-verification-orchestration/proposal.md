## Why

ZPP's complete Behave suite currently takes about two minutes, with one codespace feature dominating the runtime, while repeated all-suite verification wastes time when a change affects only a narrower capability. Nx proved locally that stable BDD target boundaries, parallel execution, and input-aware caching can reduce a cold run from about 126 seconds to 88 seconds and an unchanged rerun below one second, but ZPP needs a provider-neutral, repository-owned way to select and run only justified verification targets.

## What Changes

- Add inactive, independently selectable `bdd-structure-python`, `bdd-structure-ts`, and `bdd-structure-flutter` traits so capability ownership, feature/step organization, shared support, and runner loading boundaries follow each ecosystem's established conventions without forcing one runner across languages.
- Reorganize ZPP's own Behave suite into capability-oriented execution roots with modular step definitions and shared non-step support, enforced by structural checks, and expose those roots as independently cacheable verification targets.
- Add `zpp behave init`, `zpp behave <command>`, and `zpp behave <command> --all` repository mapping-based verification orchestration around the committed `zpp.behave.yaml`, resolving justified affected targets from the working change and running a configured first-class Nx provider or a provider-neutral typed argv template with in-place target expansion.
- Keep the committed mapping as runtime authority. Agents may help author or expand its declared target relationships, but ZPP SHALL NOT obtain an executable or command text from an agent at runtime.
- Treat unmapped and uncertain changed paths conservatively as affecting every declared target. Preserve `--all` selection of every target and separately configured audit commands for provider-specific cache validation.
- Upgrade the persistent default profile additively during user-global workflow install and update so newly packaged standard traits become available to existing users while existing user-owned files, triggers, configuration, and custom traits remain authoritative; repository-local lifecycle operations and removal do not mutate it.

## Capabilities

### New Capabilities

- `verification-orchestration`: Repository-owned named commands, affected-target mapping, safe filtered execution, provider delegation, fallback, and complete/audit verification behavior.

### Modified Capabilities

- `standard-workflow-traits`: Add optional ecosystem-specific BDD-structure traits while retaining advisory-only authority.
- `global-bootstrap-and-agent-setup`: Extend the confirmed ZPP command surface with verification orchestration without folding it into workflow-skill lifecycle management.
- `workflow-skill-distribution`: Make workflow installation upgrade the persistent default profile under an explicit conflict-safe compatibility contract.

## Impact

- Adds the `zpp behave` CLI surface for repository verification.
- Adds a committed validated repository mapping for named commands, target mappings, and provider selection, plus ignored local derived evidence.
- Adds optional packaged BDD-structure trait documents to the standard profile without adding an Nx trait or trigger.
- Introduces Nx only as an optional external executable/provider; ZPP core remains Python and does not install Nx or require it for non-Nx repositories.
- Reorganizes the repository's Behave features, step definitions, shared fixtures, and verification commands, with structural convention tests.
- Changes workflow installation's current isolation from authored profiles so the persistent default receives compatible standard-profile upgrades.

## Unresolved — Do Not Assume

None. The owner confirmed the complete behavior and workflow-distribution boundary.
