## Why

Workflow contracts, playbook instructions, runtime behavior, and verification can drift independently even when each artifact remains locally valid. Maintainers need a local, interactive audit that exercises every complete workflow separately and reports design-to-implementation mismatches without changing repository or workflow state.

## What Changes

- Package a discoverable `zpp-audit-workflows` companion skill for local workflow conformance audits.
- Discover complete workflows from the packaged JSON contract inventory rather than a duplicated workflow list.
- Assign every discovered workflow to its own subagent and run simulations in isolated temporary state.
- Compare workflow contracts, component contracts, playbook-specific instructions, runtime and CLI behavior, canonical specifications, BDD, and focused tests.
- Present one structured result per workflow and support interactive owner review or targeted reruns without editing product sources.

## Capabilities

### New Capabilities

- `workflow-auditing`: Local, read-only, per-workflow simulation and design-to-implementation conformance reporting.

### Modified Capabilities

None.

## Impact

- Adds a packaged companion skill and its UI metadata under `src/zpp/artifacts/skills/companion/`.
- Extends companion-skill packaging, lifecycle projection, and validation expectations.
- Adds capability-owned Behave scenarios, shared Python support, established step bindings, and focused Python tests.
- Adds no runtime dependency and does not change workflow reminder or Bundler lease authority.
