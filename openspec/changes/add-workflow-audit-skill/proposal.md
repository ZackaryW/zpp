## Why

Workflow contracts, playbook instructions, runtime behavior, and verification can drift independently even when each artifact remains locally valid. Maintainers need a local, interactive audit that exercises every complete workflow separately and reports design-to-implementation mismatches without changing repository or workflow state.

## What Changes

- Package a discoverable `zpp-audit-workflows` companion skill for local workflow conformance audits.
- Discover complete workflows from the packaged JSON contract inventory rather than a duplicated workflow list.
- Bootstrap one coordinator-owned temporary base Git/OpenSpec project, then clone that base into a fresh isolated repository and ZPP product home for each workflow run.
- Run exactly one workflow subagent at a time, review its result and live-state sentinels, and close or explicitly classify its recommendations before assigning the next workflow.
- Drive a synthetic change through the workflow's complete declared stage sequence and custom branches, using mock component outcomes while exercising real workflow registration and OpenSpec lifecycle surfaces.
- Compare workflow contracts, component contracts, playbook-specific instructions, runtime and CLI behavior, canonical specifications, BDD, and focused tests at every transition.
- Maintain a gap ledger and interactively close each finding by accepting a source correction, explicitly deferring it, or rejecting it. An accepted correction re-enters the affected full workflow phases and reruns that same audit from a fresh clone before the coordinator advances.

## Capabilities

### New Capabilities

- `workflow-auditing`: Local, per-workflow mock change execution and interactive design-to-implementation gap closeout.

### Modified Capabilities

None.

## Impact

- Adds a packaged companion skill and its UI metadata under `src/zpp/artifacts/skills/companion/`.
- Extends companion-skill packaging, lifecycle projection, and validation expectations.
- Adds capability-owned Behave scenarios, shared Python support, established step bindings, a reusable mock-project bootstrap helper, and focused Python tests.
- Uses existing Git, OpenSpec, ZPP, Behave, and pytest surfaces without adding a runtime dependency or changing workflow reminder or Bundler lease authority.
