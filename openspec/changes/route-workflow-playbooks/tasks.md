## 1. Verification Contract

- [ ] 1.1 Add scenario-selected routing and authority-boundary cases to the independently runnable `features/consolidated_workflow_skill/` Behave root, then run it to prove the relevant RED.
- [ ] 1.2 Add focused unit case matrices for triage classification, delegation-envelope validation, and ambiguous fallback without duplicating public integration scenarios.

## 2. Shared Workflow Components

- [ ] 2.1 Extract the shared stage, authority, Bundler, verification, checkpoint, and completion contract into packaged `zpps-workflow-kernel` with structured delegation validation.
- [ ] 2.2 Add bounded `zpps-plan` and `zpps-archive` skills that use public OpenSpec interfaces, return observed operation evidence, and reject workflow progression or authority expansion.

## 3. Workflow Entries

- [ ] 3.1 Implement thin `zpp-new-feature`, `zpp-fix-bug`, and `zpp-scaffold` entries plus the generic `zpp-workflow` entry over the shared kernel.
- [ ] 3.2 Implement non-mutating `zpp-auto` triage with unambiguous routing and generic-clarification fallback.
- [ ] 3.3 Implement policy-free `zpp-legacy-workflow` translation for the preceding consolidated invocation contract without recognizing ZPP 1.x stage skills.

## 4. Projection and Migration

- [ ] 4.1 Update packaged skill inventories and Agent Router projection expectations so the complete role-separated operation set installs together.
- [ ] 4.2 Update workflow guidance and migration documentation to describe prefix semantics, the shared `zpp-workflow` verification gate, and the legacy adapter's removal boundary.

## 5. Verification

- [ ] 5.1 Run focused unit tests and the `features/consolidated_workflow_skill/` root independently, then run the relevant complete native test surface.
- [ ] 5.2 Run the repository's supported-interpreter, lock, lint, format, and clean package-build gates through the declared build backend.
- [ ] 5.3 Strictly validate the OpenSpec change and inspect a projected installation to confirm every entry reaches one kernel and no generated OpenSpec skill is required as workflow authority.
