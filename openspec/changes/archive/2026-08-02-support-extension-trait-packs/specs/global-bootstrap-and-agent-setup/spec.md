## MODIFIED Requirements

### Requirement: Source-authoritative lifecycle context
Every installed native lifecycle integration SHALL identify its owning Codex, Claude, or Pi agent when resolving traits for the agent session's current working directory at invocation time. Resolution SHALL use that identity to discover only the invoking agent's active plugin trait sources. Successful non-empty resolution output SHALL be injected exactly once into the current agent context. Empty successful output SHALL inject nothing. Resolution failure SHALL be surfaced through the agent and SHALL inject no stale or partial ZPP context.

Agent installation itself SHALL NOT invoke resolution, discover plugin trait sources, or create trait caches.

#### Scenario: Invoke a configured lifecycle integration
- **WHEN** a configured and enabled native lifecycle event invokes ZPP
- **THEN** it identifies the owning agent, injects current successful trait output once, injects nothing for empty output, and contributes no stale or partial context after failed resolution

#### Scenario: Keep agent installation side-effect free from resolution
- **WHEN** ZPP installs or reconciles a native lifecycle integration
- **THEN** it does not resolve traits, inspect active plugin sources, or create derived trait state during installation
