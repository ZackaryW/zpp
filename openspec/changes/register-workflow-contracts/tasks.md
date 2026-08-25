## 1. Executable Workflow Contract

- [x] 1.1 Add capability-owned Behave scenarios and direct CLI bindings for strict contract inventory loading, idempotent workflow start/resume, stage customization, sequence reminders, accepted-result progress, stop behavior, standalone untracked component use, and prompt-submission reminder-hook silence/read-only behavior.
- [x] 1.2 Add trace-only conformance anchors for the new `workflow-registration` scenarios and the modified consolidated workflow scenarios without duplicating executable GIVEN/WHEN/THEN behavior in OpenSpec.

## 2. Packaged JSON Contract Utilities

- [x] 2.1 Write focused RED unit tests for strict versioned workflow/component JSON decoding, unknown-field and invalid-type rejection, duplicate detection, and cross-reference failures.
- [x] 2.2 Implement immutable workflow and component contract models plus strict JSON decoders using the repository's artifact-loading conventions.
- [x] 2.3 Add workflow and component JSON schemas and package them as discoverable artifacts with typed resource access.
- [x] 2.4 Write RED inventory tests requiring one contract for every complete current `zpp-*` playbook and every packaged `zpps-*` component, valid stage references, and no obsolete `zpp-workflow` identity.
- [x] 2.5 Add the complete workflow/component contract inventory and replace Markdown-derived stage-order validation with JSON contract validation.

## 3. Reminder State Utilities

- [x] 3.1 Write focused RED tests for exact-target workflow start, idempotent resume, different-workflow preservation, persisted stage states, and product-home isolation.
- [x] 3.2 Implement immutable active-run and stage-state models plus atomic product-home reminder persistence without acquiring or mutating Bundler leases.
- [x] 3.3 Write RED tests for insert, delete, modify, and idempotent upsert validation, including invalid positions, duplicate IDs, and unknown components.
- [x] 3.4 Implement direct checklist customization and stop operations with whole-candidate validation before atomic replacement.
- [x] 3.5 Write RED tests for in-sequence and out-of-sequence checks, accepted matching result progress, ignored blocked/unrelated/read-only results, and optional observed bundle association.
- [x] 3.6 Implement reminder comparison and accepted-result recording with structured `allowed`, `sequence_match`, expected-stage, unfinished-stage, and warning evidence.

## 4. Workflow Run CLI

- [ ] 4.1 Add the nested `zpp workflow run` and `zpp workflow run stage` Typer groups without changing existing workflow install, update, or remove behavior.
- [ ] 4.2 Implement structured `start`, `status`, and `stop` commands over the selected product home and exact repository/change targets.
- [ ] 4.3 Implement the prompt-facing read-only `remind` command with exact repository resolution, compact active output, silent inactive output, and no state creation or transition.
- [ ] 4.4 Implement structured `check` and `record` commands for kernel consumption, including `workflow-start-required`, untracked direct invocation, and warning-only mismatch results.
- [ ] 4.5 Implement structured stage `insert`, `delete`, `modify`, and `upsert` commands with stable IDs and explicit before/after positioning.
- [ ] 4.6 Complete the public CLI Behave bindings and focused integration tests for cross-process persistence and unchanged lease state.

## 5. Kernel and Skill Integration

- [ ] 5.1 Update `zpps-workflow-kernel` to require registration for identified complete playbooks, surface reminder checks for active targets, and record only accepted matching stage results without selecting continuation.
- [ ] 5.2 Update each complete current `zpp-*` skill to start its registered workflow before lifecycle work and retain only its custom agreement, stage configuration, and branch conditions.
- [ ] 5.3 Update each packaged `zpps-*` skill to retain substantive readiness, procedure, failure, and stopping behavior while removing mechanical metadata now owned by its JSON contract and shared kernel behavior.
- [ ] 5.4 Update `zpp-auto` and compatibility coverage so handoff enters the selected playbook's registration and genuine no-handoff/direct artifact routes create no reminder state.
- [ ] 5.5 Verify every installed skill projection contains the compact composed contract guidance and that packaging rejects missing, mismatched, or extra JSON/Markdown identities.
- [ ] 5.6 Add the separate `zpp-workflow-reminder` hook artifact for adapters with an explicitly confirmed prompt-submission context event, and compose its Agent Router-owned projection, inspection, update, and removal into the shared lifecycle inventory without changing `zpp-traits`.
- [ ] 5.7 Add focused artifact and lifecycle tests proving unsupported adapters omit the hook, supported adapters use their declared event form, inactive invocation is silent, active output is compact, and invocation changes no reminder or lease state.

## 6. Repository Verification

- [ ] 6.1 Run the scenario-selected workflow-registration Behave targets and all focused artifact, product-home, workflow-coordination, reminder-state, and CLI tests.
- [ ] 6.2 Run formatting, lint/type checks, the complete Python test suite, and clean package build through the repository's established runners.
- [ ] 6.3 Validate packaged JSON with the strict schemas and structured parsers, then run strict OpenSpec validation and semantic change verification.
- [ ] 6.4 Confirm no workflow reminder operation changes Bundler members or lease lifecycle and no out-of-sequence reminder returns a blocking result in reminder mode.
- [ ] 6.5 Confirm lifecycle operations reconcile the conditional reminder hook only through Agent Router and that hook execution never creates or advances workflow state.
