## Why

The current `zpp-workflow` concentrates every outcome, seven stage contracts, OpenSpec operations, verification, dependency policy, coordination, and completion into one large generic skill while generated OpenSpec skills and packaged traits repeat parts of that control surface. ZPP needs complete outcome-specific Markdown playbooks that make their own ordered sequences and conditions visible while reusing singular bounded components and one lifecycle-control kernel.

## What Changes

- **BREAKING** Rename the current generic `zpp-workflow` playbook to `zpp-legacy-workflow` and remove the `zpp-workflow` skill identity without an alias.
- Package `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, and `zpp-legacy-workflow` as complete ordered Markdown playbooks. Each playbook interleaves workflow-specific custom instruction blocks with explicit configured uses of exact `zpps-*` components and owns the sequence and branch conditions for its outcome.
- Add `zpp-auto` as a complete non-mutating triage playbook: it performs its ordered classification, may explicitly use read-only `zpps-explore`, then invokes exactly one of `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow` with the original request and supplied authority; mixed or unresolved work invokes the legacy playbook at `clarify`. It SHALL NOT merely report the selected playbook and stop.
- Extract transition eligibility, mutation authority, Bundler progression, checkpoint handling, changed-path post-result audit, component-result assessment, and truthful completion into `zpps-workflow-kernel`. The kernel validates the playbook-requested transition but never chooses, reorders, or advances the playbook sequence. Automatic continuation means only that the active playbook follows its declared branches; it never answers an unresolved decision or supplies missing owner, mutation, checkpoint, or archive authority.
- Decompose current stage behavior into substantive `zpps-clarify`, `zpps-shape-bdd`, `zpps-planning-ponytail`, `zpps-mature-utilities`, `zpps-wire`, `zpps-form-specs`, and `zpps-finalize` skills. Each contains its complete bounded procedure, accepts explicit configuration from a playbook or direct partial invocation, and returns its own result without selecting lifecycle continuation.
- Add eleven substantive OpenSpec adapter skills: `zpps-explore`, `zpps-new-change`, `zpps-continue-change`, `zpps-ff-change`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-verify-change`, `zpps-sync-specs`, `zpps-archive-change`, and `zpps-bulk-archive-change`. Each preserves the complete upstream operation procedure, state and instruction discovery, stopping boundary, outputs, and failure behavior while applying ZPP's Bundler and single-BDD-authority constraints. Fast-forward always scaffolds a new change and reports a collision for separately selected continue behavior; standalone propose stops after planning while an authorized playbook may consume that result and follow its next declared branch; verify-change returns `repository-evidence-required` instead of invoking the repository verifier; archive retains only its synchronous sync sub-operation. Explicitly exclude onboarding because it is an instructional walkthrough rather than an operational primitive.
- Add `zpps-verify-repository` as a separate executable-evidence component rather than an OpenSpec adapter.
- **BREAKING** Remove the complete OpenSpec skill-install surface from ZPP: temporary repository generation, `openspec init` invocation, generated-skill inventory validation, provenance stamping, generation-only version detection, lifecycle projection, repair, and reporting. Root `zpp init`, `zpp sync`, and `zpp reset` invoke no OpenSpec process; each ZPP-owned adapter validates the installed executable and required public interface only when its bounded operation runs.
- Move Ponytail, zero-assumption reconciliation, complete build gates, BDD binding invariants, verification truthfulness, and shared RED/GREEN rules from packaged traits into their owning skills.
- Give every testable public-system obligation one acceptance authority: `zpps-shape-bdd` transfers concrete scenarios into the capability-owned feature root, `zpps-form-specs` replaces duplicated OpenSpec examples with trace-only conformance anchors, and `zpps-verify-change` rejects duplicate or orphaned authority.
- Require an exact registered store UUID and change member, resolved from the public store list, before every governed mutation. Repo-local OpenSpec roots remain valid for read-only discovery and verification and for resolving existing `repo:` trace locators, but cannot acquire the current Bundler lease; mutation returns `store-registration-required`. Bundler membership contains only exact store/change members, while components return exact changed paths for kernel post-result audit.
- **BREAKING** Remove the packaged `dependencies`, `build`, and `zero-assumptions` trait families; narrow `bdd`, `bdd-execution`, and `tdd` to contextual language, framework, and mode specialization; retain `bdd-structure` and `tooling` as contextual traits.
- Replace the obsolete `zpp-workflow` behavior-gate identity with the shared `zpps-workflow-kernel` gate and provide no former-gate translation.
- Overhaul lifecycle projection around one scope-aware reconciliation operation over both the current packaged inventory and an exact finite obsolete-identity inventory. Explicit root initialization and synchronization operate at user scope, while grouped workflow update operates at its selected user or project scope. Reconciliation installs and verifies the current family before retiring only Agent Router-owned obsolete projections, preserves unowned collisions, and reports partial failure truthfully instead of claiming a complete migration.
- Treat a machine containing only owned prior-version projections as an installed ZPP that can be migrated by explicit lifecycle commands: root `zpp init` recognizes and reconciles that old-only user installation, root `zpp sync` migrates it in user scope, and `zpp workflow update` migrates it in the same selected scope. `zpp workflow install` remains a first-install operation and preflights conflicts rather than failing after projecting a prefix of the family.
- Keep OpenSpec Bundler as a library-only ZPP dependency with no executable or separate tool installation. The built ZPP distribution SHALL be the sole `uv tool` installation, expose the `zpp` command, carry one package version consistent with `zpp.__version__` and `zpp --version`, and install Bundler only inside ZPP's environment as a dependency.
- Supersede the narrower planning intent in `route-workflow-playbooks`; that change remains untouched until separately retired.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `automatic-trait-hooks`: Reconcile grouped installation and removal with the complete deterministic packaged workflow family plus the `zpp-traits` hook.
- `consolidated-workflow-skill`: Replace one monolithic workflow skill with complete outcome-specific Markdown playbooks, one transition-control kernel, bounded stage and operation components, and skill-owned invariant policy.
- `openspec-bundler-integration`: Assign automatic lease acquisition and progression to the active complete playbook or directly invoked mutating component through the guard-only kernel, with no removed workflow identity.
- `openspec-maintenance-skill`: Route maintenance operations through current ZPP-owned adapters and current playbook authority rather than generated upstream OpenSpec skill identities.
- `openspec-skill-provisioning`: Replace generated upstream OpenSpec operation skills with the complete packaged ZPP workflow skill family.
- `product-home-lifecycle`: Change the shared initialization, synchronization, and reset inventory to the new hard-cut skill identities.

## Impact

- Packaged workflow playbook, phase, adapter, verification-component, and companion skill assets and their Agent Router projections.
- Removal of `zpp.utils.openspec`, generated-entry construction, and OpenSpec-specific branches in initialization, synchronization, reset, reporting, tests, and Behave support.
- Packaged trait inventory and the division between invariant skill policy and contextual trait specialization.
- Consolidated-workflow, automatic-trait-hooks, and lifecycle Behave roots, artifact inventory unit tests, and projected-installation verification.
- OpenSpec-to-BDD traceability and the rule that no completed shaping or specification-formation stage leaves the same executable acceptance example in both artifact systems.
- Bundler and OpenSpec-maintenance canonical authority names, including removal of stale normative references to the deleted workflow and generated operation-skill identities.
- Repository `zpp.behave.yaml` mappings that currently name the removed `zpp-workflow` gate must adopt `zpps-workflow-kernel`.
- No OpenSpec executable installation or lifecycle preflight, trait document format, Bundler lease format, or compatibility alias is introduced.
- Existing user- and project-scope installations, package metadata, CLI version reporting, and built-distribution tool exposure participate in the migration verification surface.
