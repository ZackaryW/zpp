## Why

ZPP promises automatic Bundler acquisition, but mutating workflow components currently expose store registration, store UUID bootstrap, and a caller-supplied durable owner as user decisions. The resulting prompts block otherwise authorized work and make the coordination layer part of the product workflow instead of an internal safety mechanism.

## What Changes

- Let an owner-authorized mutating workflow automatically register its resolved repo-local OpenSpec root when no matching store registration exists.
- Add an idempotent ZPP runtime boundary that registers roots, creates or validates store-owned Bundler UUID manifests, retains one product-home workflow identity, and drives exact lease acquisition through completion.
- Let `ZPP_WORKFLOW_COORDINATION` strictly override automatic owner and store selection while keeping a valid exact-member lease mandatory.
- Keep skills declarative: the workflow kernel and mutating `zpps-*` components invoke the ZPP runtime and consume its structured result without implementing registration, identity, environment, or lease logic themselves.
- Add a separate explicit `zpp bypass` command for an owner-approved one-command unleased escape hatch; require a reason, scope bypass to the child process, and visibly warn whenever it runs.
- Preserve explicit owner/UUID input and the minimal lease bridge for diagnostics and recovery, and continue surfacing genuine registration, manifest, topology, ownership, and lease conflicts.
- Prove the seamless path through capability-owned BDD and focused Python tests without weakening archive authority, mutation authority, or bundle safety.

## Capabilities

### New Capabilities

- `workflow-coordination-bypass`: Provide an explicit, visibly warned, one-command escape hatch for owner-approved unleased execution.

### Modified Capabilities

- `openspec-bundler-integration`: Make store bootstrap and durable workflow ownership automatic behind ZPP's guarded mutation boundary while preserving exact Bundler membership and conflict safety.
- `consolidated-workflow-skill`: Remove internal store, UUID, owner, and lease questions from authorized playbook and direct-component execution.

## Impact

- ZPP product-home identity state, runtime coordination service, Bundler adapter/CLI behavior, and bypass command.
- Packaged workflow-kernel, playbook, stage, and mutating OpenSpec component instructions.
- OpenSpec Bundler integration and consolidated-workflow BDD roots, bindings, support, and focused unit tests.
- Canonical specifications and user documentation for automatic workflow coordination, strict environment overrides, explicit recovery controls, and warned bypass execution.
