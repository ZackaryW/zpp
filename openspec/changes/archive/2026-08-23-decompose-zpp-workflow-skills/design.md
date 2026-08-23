## Context

See `proposal.md` for motivation. The current package exposes one workflow asset through a singular artifact loader, generates six OpenSpec operation skills during initialization and synchronization, projects them beside `zpp-workflow`, and repeats invariant workflow rules across the skill and eight packaged trait families. The current lifecycle inventory is shared by initialization, synchronization, and reset, so the replacement must change packaging, projection, obsolete-asset cleanup, and workflow behavior atomically.

## Goals / Non-Goals

**Goals:**

- Make each `zpp-*` workflow a complete ordered Markdown playbook that owns its outcome-specific sequence and branch conditions.
- Make the kernel small enough to express only transition eligibility, mutation authority, Bundler progression, checkpoint handling, component-result assessment, and truthful completion without selecting a sequence.
- Give every stage one substantive bounded skill whose complete procedure can run from playbook-supplied configuration or an explicit direct partial invocation.
- Delete ZPP's complete OpenSpec skill-generation and installation subsystem and replace runtime operations with ZPP-owned adapters over public OpenSpec interfaces.
- Move invariant control policy into skills while preserving contextual language, framework, structure, mode, and tooling specialization in traits.
- Reconcile existing owned installations to the new inventory without adopting or deleting unowned native assets.

**Non-Goals:**

- Add aliases for `zpp-workflow`, its behavior gate, generated `openspec-*` skills, or ZPP 1.x stage skills.
- Persist a new workflow-state file or turn the delegation envelope into a public serialization format.
- Replace the OpenSpec executable, Bundler lease format, Agent Router, zmem companions, or repository-owned behavior mappings.
- Encode packaged prose as BDD or unit-test assertions.
- Factor the ordered workflow sequence into the kernel, a shared reference, or an implicit convention that leaves a `zpp-*` playbook incomplete.

## Decisions

### Split playbook sequencing, lifecycle control, stages, and operations

The package will use four distinct roles:

| Role | Skills | Owns |
|---|---|---|
| Workflow playbooks | `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, `zpp-legacy-workflow` | User trigger, complete ordered sequence, workflow-specific custom instructions, branch conditions, and explicit component uses |
| Lifecycle control | `zpps-workflow-kernel` | Requested-transition eligibility, mutation authority, Bundler, checkpoints, component-result assessment, and truthful completion |
| Stage skills | `zpps-clarify`, `zpps-shape-bdd`, `zpps-planning-ponytail`, `zpps-mature-utilities`, `zpps-wire`, `zpps-form-specs`, `zpps-finalize` | One current-stage output and its evidence |
| OpenSpec adapters | `zpps-explore`, `zpps-new-change`, `zpps-continue-change`, `zpps-ff-change`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-verify-change`, `zpps-sync-specs`, `zpps-archive-change`, `zpps-bulk-archive-change` | One public OpenSpec operation and its observed result |
| Repository evidence | `zpps-verify-repository` | Execute declared native repository verification and return truthful evidence |

Every skill is a real Agent Router asset, but packaging does not grant lifecycle authority. Playbook descriptions identify user-facing triggers and each playbook contains its complete ordered procedure. The kernel acts when a playbook or directly invoked component requests transition assessment or lifecycle control. Stage and operation descriptions identify their bounded inputs and forbid workflow selection or continuation, but their instruction bodies contain the complete procedure rather than forwarding work to the kernel.

This keeps reusable operation bodies singular without hiding the user-visible workflow. Copying the complete sequence into each outcome playbook is intentional: a playbook remains understandable and runnable when loaded alone, while the exact `zpps-*` use steps prevent the bounded component contracts from being copied.

### Represent each workflow as a complete ordered Markdown playbook

Every `zpp-*` asset is a complete playbook, not a thin router or a list of references. Its Markdown sequence interleaves two kinds of ordered blocks:

- workflow-specific custom instruction blocks containing outcome framing, decisions, or handling that belongs only to that playbook;
- configured component-use blocks naming one exact `zpps-*` skill, the condition under which it is used, the inputs and accepted evidence passed to it, the kernel assessment required before or after the use, and the result status consumed by the next declared playbook condition.

The block layout is a documented Markdown convention, not a new public serialization or runtime parser. A playbook SHALL state every possible next playbook step and branch condition directly. It may reuse the same `zpps-*` component as another playbook, but it may not defer its sequence to the kernel or to a shared hidden stage list.

`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, and `zpp-legacy-workflow` each carry their complete applicable lifecycle from initial clarification through finalization. Their custom blocks and conditions may differ even when their configured component uses overlap. `zpp-auto` is complete for non-mutating triage: it performs its ordered classification, may use `zpps-explore` for read-only evidence, and terminates by handing off exactly once to one complete outcome playbook. It never inherits the selected playbook's sequence as its own or performs governed mutation.

For a component step, the active playbook first asks `zpps-workflow-kernel` to assess the transition it has selected. The kernel returns an eligible, blocked, completed, or accepted-not-applicable assessment and performs any authorized lease or checkpoint control. The playbook then follows its already declared condition: it uses the exact component when eligible, pauses when blocked, or selects the next step named by the playbook when the prior result is accepted. The kernel never returns a next-stage choice. Automatic continuation authorizes only this traversal of already declared branches; it cannot answer an unresolved decision or create missing owner, mutation, checkpoint-commit, or archive authority. A direct partial invocation supplies the component's required configuration itself; read-only work proceeds without a kernel round trip, while governed mutation presents an existing valid assessment or asks the kernel for the required guard and lease. Absence of a prior kernel delegation is therefore not, by itself, a reason to reject the component invocation.

### Rename the current semantic fallback rather than retain its identity

The current generic outcome moves to `zpp-legacy-workflow`; there is no `zpp-workflow` identity after migration. The legacy playbook does not retain the current monolithic component bodies. It retains the complete generic sequence and outcome-specific custom instructions while using the same bounded kernel, phase skills, and adapters available to the other complete playbooks.

`zpp-auto` invokes exactly one clear outcome playbook and otherwise invokes `zpp-legacy-workflow` at `clarify`. The invocation passes the original request, accepted read-only classification evidence, and only authority already supplied by the owner. Control transfers to that selected playbook exactly once; `zpp-auto` does not return to classify again, merely name the route and stop, mutate, or fill missing authority fields. This preserves a generic workflow without leaving two names for it.

### Use a logical delegation envelope without new persisted state

The active playbook passes the kernel a logical envelope for one requested transition containing:

- selected workflow outcome;
- repository roots and any already resolved store/change targets;
- playbook-selected current and requested component step;
- accepted owner input;
- owner authorization for automatic playbook continuation through declared branches;
- checkpoint-commit authority.

Repository roots must be known before inspection. A repo-local OpenSpec root remains valid for read-only discovery and verification and for resolving an existing `repo:` trace locator. Before any governed mutation, however, `openspec store list --json` must resolve an exact registered store UUID and the exact change member; otherwise the component returns `store-registration-required` and remains blocked. The Bundler bundle identity exists only after acquisition and contains store/change members, never filesystem, repository, canonical, or archive paths. Components return every exact changed path so the kernel can post-audit the result against the accepted operation. The kernel validates only the fields needed by the playbook-requested action and never infers, reorders, or returns a later step or extra authority from repository state.

The envelope remains skill-to-skill prompt state. Existing OpenSpec artifacts, Bundler state, checkpoint commits, and current repository evidence remain the durable sources used to reassess a later invocation.

### Make every stage skill a substantive bounded procedure

Each stage skill is independently usable from either a configured component-use block in a playbook or a direct partial invocation. Its Markdown body defines its own trigger, required inputs, input-resolution rules, ordered operation, stopping boundary, result fields, and failure behavior. A playbook passes accepted contract state and any existing kernel assessment; a direct caller passes the same operation-specific values explicitly. The skill SHALL ask only for missing values that are required for its own bounded result and SHALL NOT reject merely because no playbook or kernel delegated it.

Read-only stage work runs directly, including inspection through a repo-local OpenSpec root. Before governed mutation, the stage skill requires a public-store-list-resolved UUID, the exact change member, a still-valid kernel assessment, and the Bundler lease containing that member, either supplied by the playbook or obtained by requesting that guard itself. Without the registered UUID it returns `store-registration-required`; changed paths are never lease members. This request does not let the kernel choose the component or its procedure. Each stage skill returns a declared `completed`, `blocked`, `store-registration-required`, or eligible `skipped: not applicable` outcome plus every exact changed path for kernel post-audit, unresolved questions, and verification evidence. A mutating stage may mark only supplied OpenSpec tasks whose complete behavior its successful work and evidence fully satisfy; it never checks off a partial, unrelated, or merely attempted task. It does not select the next playbook step, expand authority, complete a checkpoint, or claim lifecycle completion.

- `zpps-clarify` resolves roots and current evidence, reconciles the request against repository reality and prior owner decisions, asks only outcome-changing questions, records the accepted agreement revision, and stops at agreement or an explicit unresolved question. It returns any separate read-only investigation or planning-operation need without performing that other operation.
- `zpps-shape-bdd` classifies accepted obligations by public observability, locates the capability-owned feature root, and resolves existing repo-local bindings during read-only inspection. Creating or changing a feature/spec binding is governed mutation and therefore requires the exact registered store UUID/change member. It transfers each executable example and its exact registered-store binding, establishes the independently runnable RED surface, preserves non-observable policy as specification-only content, and stops with binding and RED evidence or a concrete shaping blocker.
- `zpps-planning-ponytail` assesses utility applicability, walks the ordered reuse-through-package ladder, defines signature-level boundaries, performs package comparison only when that rung is reached, and returns a disposable utility plan or the exact unresolved utility decision without implementation.
- `zpps-mature-utilities` selects the relevant planned utility, proves focused RED, implements the smallest coherent slice, proves focused GREEN and complete utility verification, and returns changed paths and evidence or stops on a plan/design mismatch.
- `zpps-wire` resolves the accepted public composition points, applies capability-local integration bindings, runs focused composition verification, and returns the wired surface and evidence without selecting specification or finalization work.
- `zpps-form-specs` resolves exact BDD targets and OpenSpec roots, performs the bidirectional semantic authority audit, removes duplicated executable examples while preserving trace-only conformance anchors, and returns synchronization eligibility. After the caller explicitly uses `zpps-sync-specs`, a second direct invocation performs the canonical authority audit.
- `zpps-finalize` validates and assembles the supplied `zpps-verify-repository`, `zpps-verify-change`, and single or bulk archive results, reports any missing or insufficient evidence, and returns a finalization assessment. The kernel retains archive-result assessment, bundle completion, and checkpoint authority.

The kernel invokes `zmem-author-commits` only while carrying out an authorized checkpoint after assessing a material completed component result, preserving the existing selective annotation and commit-authority boundary without choosing the next playbook step.

### Make OpenSpec adapters substantive and procedure-complete

ZPP packages one bounded adapter for each operational upstream OpenSpec workflow except onboarding: exploration; new, continue, fast-forward, propose, update, apply, verify, sync, single archive, and bulk archive. `openspec-onboard` is recorded as explicitly excluded because narrated teaching is not a component operation. The prior broad `zpps-plan-change`, `zpps-verify`, and `zpps-archive` identities do not exist.

An adapter is not a conceptual alias for an upstream skill and is not a thin request for kernel dispatch. Its packaged Markdown body preserves the upstream operation's complete input selection, registered-store handling, repo-local fallback, status and instruction discovery, context and rule consumption, ordered work, prompts and stopping boundary, output summary, and failure behavior. ZPP tailors those procedures only where its controlling contracts require Bundler authority, OpenSpec-to-BDD single authority, the onboarding exclusion, the prohibition on `openspec init` and generated skills, or the hard cut from prior identities.

The required operation preservation is:

| Adapter | Complete bounded procedure and stopping boundary |
|---|---|
| `zpps-explore` | Resolve the applicable store or repo-local root, inspect active changes and project context, investigate conversationally, and remain read-only; an explicit request to capture planning is returned as a need for the corresponding planning adapter. |
| `zpps-new-change` | Resolve intent and schema, scaffold through `openspec new change`, read structured status and the first ready artifact instructions, report the template, and stop before creating an artifact. |
| `zpps-continue-change` | Resolve or prompt for one change, inspect schema status, create exactly the first ready artifact from current instructions and freshly read dependencies, report new status, and stop after one artifact. |
| `zpps-ff-change` | Resolve understood intent and always scaffold one new change, compute the complete transitive apply-required artifact set, create it in dependency order from current instructions and dependencies, honor explicit skips, and stop when implementation prerequisites are ready. If the change name already exists, return the collision and require the caller to select `zpps-continue-change` separately rather than converting fast-forward into continuation. |
| `zpps-propose-change` | Reconcile material ambiguity, scaffold one change, create the full transitive planning set coherently from current instructions and dependencies, and stop at planning without implementing. A standalone invocation always stops there; an owner-authorized active playbook may consume the proposal result and follow its already declared next branch. |
| `zpps-update-change` | Resolve one existing change, use status-reported existing output paths, revise only existing planning artifacts with coherent owner-approved edits, and never create a missing artifact or edit product code. |
| `zpps-apply-change` | Resolve one change, load apply instructions and every reported context file, implement pending tasks incrementally, mark only supplied tasks whose behavior and evidence are fully complete, and continue until complete or an explicit ambiguity, design issue, error, or scope blocker requires a pause. |
| `zpps-verify-change` | Resolve one change and all apply context, assess task/spec completeness, requirement and scenario correctness, and design/repository coherence, then return a severity-ranked actionable report without mutation. When required native evidence is missing or stale, return `repository-evidence-required` with the exact requested surface; do not invoke `zpps-verify-repository`. |
| `zpps-sync-specs` | Resolve only status-reported delta paths, obtain the current specs-rule snapshot, semantically and idempotently merge selected deltas into store-aware canonical specs while preserving unaffected content, validate, and leave the change active. |
| `zpps-archive-change` | Resolve one active change, load advisory archive inputs, inspect artifact/task completion, assess and optionally perform synchronous semantic sync with post-sync verification, then move the change only after the chosen checks and report warnings and result. |
| `zpps-bulk-archive-change` | Require explicit multi-selection, collect every change's status/tasks/deltas, resolve exact-capability conflicts from implementation evidence, confirm once, prefetch every required rule snapshot atomically, synchronously sync and verify included deltas, archive each eligible change, and report success, skip, sync-skip, and failure separately. |

Each adapter can receive its operation configuration from a playbook or a direct partial invocation. Read-only adapters run without a kernel delegation and may use a repo-local root. Before mutation, an adapter must resolve the exact registered store UUID from the public store list and obtain a guard/lease for only that UUID/change member; otherwise it returns `store-registration-required`. Filesystem paths are not lease members. Adapters return resolved roots, store/change identities, every exact changed path for kernel post-result audit, unresolved questions, progress or assessment state, and observed evidence. They never ask the kernel which operation to run, select a workflow stage, expand a lease, grant checkpoint or commit authority, infer lifecycle continuation, or claim lifecycle completion. The archive adapters may invoke `zpps-sync-specs` synchronously only where their preserved upstream procedure makes sync an explicit selected sub-operation; that bounded composition does not grant general continuation authority.

Adapters never run `openspec init` or consume generated `openspec-*` skills. Each adapter checks executable availability and exactly the public interfaces needed by its operation at invocation time; root initialization, synchronization, and reset perform no OpenSpec detection, version check, initialization, generation, or other process invocation. Where an upstream procedure recognizes legacy CLI response fields, the ZPP adapter targets the current supported interface only and carries no compatibility branch for superseded ZPP or Bundler behavior.

### Delete the OpenSpec skill-install subsystem

The implementation removes `zpp.utils.openspec` in full. Its six-name generated inventory, generation exception, provenance model and writer, process and runner abstractions, version detector, temporary-repository contexts, generated-skill loaders, agent-relative path mapping, and exports exist only to install upstream skills and have no surviving runtime caller.

Root initialization removes `generated_openspec_skill_sets` and projects only the packaged workflow family, hook, and companions. Synchronization removes its second generated-entry inspection/projection pass, and `zpp.cli.lifecycle` removes `generated_entries`. Reset derives current packaged entries plus an explicit removal-only obsolete inventory; the six former generated names remain tombstones only so Agent Router can remove a projection it can prove ZPP-owned. Tombstones carry no content, provenance writer, generator, repair, version, or installation behavior.

The former `features/openspec_skill_provisioning/` capability root is retained but reauthored around packaged adapter projection, lifecycle independence from the OpenSpec process, and absence of generated assets. Generation-only unit tests in `tests/unit/test_openspec.py` are deleted. CLI, reset, artifact, lifecycle, and end-to-end tests are revised to prove packaged inventory and ownership-safe tombstone cleanup without mocking or invoking OpenSpec generation.

### Keep executable acceptance in one artifact authority

OpenSpec strict validation currently requires every requirement to contain a `#### Scenario`, while ZPP requires concrete public-system acceptance examples to be executable through capability-owned BDD. ZPP therefore distinguishes a concrete acceptance example from a trace-only conformance scenario. The latter satisfies the OpenSpec structural contract without restating the executable GIVEN/WHEN/THEN behavior.

During clarification, an OpenSpec scenario may be a provisional acceptance example while no BDD authority exists. `zpps-shape-bdd` classifies each obligation. A testable public-system obligation is transferred into `features/<capability>/<capability>.feature`, bound to the exact OpenSpec store, capability, and requirement identity, and implemented through the capability-local support entry point and thin bindings. The same completed shaping action replaces the concrete OpenSpec example with a conformance scenario that points to the bound feature identity and contains no duplicate behavioral steps. A pure-functionality case matrix belongs in unit tests, retaining one public end-to-end BDD scenario when needed to prove enforcement. An obligation with no executable public-system observation remains normative OpenSpec requirement content rather than being fabricated as BDD.

The binding identity is the exact five-value tuple `root`, `capability`, `requirement`, `feature`, and `scenario`; ZPP does not mint a binding UUID. Both sides encode that tuple as compact JSON with keys in that order. The feature side places the following declaration immediately above the bound scenario:

```gherkin
# zpp-spec: {"root":"<root-id>","capability":"<capability-id>","requirement":"<exact-requirement-heading>","feature":"<git-root-relative-feature-path>","scenario":"<exact-scenario-name>"}
Scenario: <exact-scenario-name>
```

`root` is `store:<uuid>` only when that exact UUID was returned by `openspec store list --json`; a store name, filesystem basename, or generated UUID is never substituted. Creating or changing a binding during shaping is governed mutation and therefore uses that exact registered-store locator. An existing binding may retain a nearest repo-local locator, `repo:<git-root-relative-path-to-openspec-root>` with forward slashes such as `repo:openspec`, and read-only shaping/forming/verification may resolve it without registration; this does not authorize mutation or automatic migration of the locator. `capability` is the exact OpenSpec capability directory identity, `requirement` is the exact text after `### Requirement:`, `feature` is the normalized Git-root-relative feature path, and `scenario` is the exact Gherkin scenario title. The corresponding trace-only OpenSpec conformance scenario repeats the identical JSON tuple and names `<feature>::<scenario>` as its executable target. Repeating this metadata is bidirectional traceability, not duplicated acceptance behavior.

A tuple resolves only when the feature declaration is immediately adjacent to exactly one scenario, the feature path and scenario title resolve uniquely, the root resolves by the declared locator kind, and the target requirement contains the identical tuple. Repo-local and registered-store locators are mutually exclusive. Moving a repo-local OpenSpec root, renaming a requirement, moving a feature, or renaming a scenario requires updating both declarations atomically; ZPP never guesses the replacement.

`zpps-form-specs` performs a semantic, not merely textual, authority audit before synchronization. Every executable obligation must have one or more bound feature scenarios and no concrete OpenSpec acceptance duplicate; every spec-only obligation must have no feature claiming its authority; and every binding must resolve in both directions. It returns synchronization eligibility; the playbook explicitly uses `zpps-sync-specs`, then explicitly uses `zpps-form-specs` for the canonical audit. `zpps-verify-repository` runs scenario-selected BDD, focused tests, relevant complete tests, interpreter and lock checks, lint, format, and a clean build. The playbook passes that evidence to its explicit `zpps-verify-change` use for the final cross-artifact audit. When evidence was not supplied or is insufficient, verify-change returns `repository-evidence-required` to the caller rather than invoking the repository verifier; neither component chooses continuation or lifecycle completion.

This keeps the upstream operation procedure inside each substantive adapter while each ZPP playbook owns its visible continuation sequence. The adapter is complete for its bounded operation, but it never becomes a second top-level workflow boundary.

### Migrate invariants and retain only contextual traits

The migration follows an ownership test: a rule that must hold for every repository belongs to a skill; a rule selected by language, framework, repository mode, structure, or available tooling may remain a trait.

| Current family | Result | New owner |
|---|---|---|
| `dependencies` | Remove | `zpps-planning-ponytail` |
| `zero-assumptions` | Remove | kernel and `zpps-clarify` |
| `build` | Remove | `zpps-verify-repository` |
| `bdd` | Retain contextual runner/layout bodies only | invariants in `zpps-shape-bdd` |
| `bdd-execution` | Retain selected mode only | truthfulness and command boundary in `zpps-verify-repository` |
| `tdd` | Retain language/framework advice only | shared RED/GREEN in `zpps-mature-utilities` |
| `bdd-structure` | Retain | contextual structure |
| `tooling` | Retain | contextual available-tool preference |

Retained bodies are edited rather than wrapped around copied invariants. This prevents an injected trait from restating or weakening the phase contract.

### Replace singular packaging and generated provisioning

The artifact loader changes from one packaged workflow skill to a deterministic workflow-family collection. Initialization, synchronization, reset, inspection, and reporting all consume the same packaged collection. The OpenSpec generation module and every live caller are removed in the same implementation slice; only the lifecycle tombstone identities survive as inert cleanup data.

The current projection order is complete playbooks, kernel, phase and operation skills, `zpp-traits`, then remaining companions. Agent Router remains the only native-destination authority.

An explicit finite tombstone inventory contains `zpp-workflow` and the six formerly generated identities. No prefix, glob, directory sweep, or inferred prior-version name expands that inventory. Every lifecycle caller passes an exact `Scope` and, for project scope, an exact project root to the same current-plus-obsolete reconciliation primitive. A tombstoned projection is removed only when Agent Router confirms ZPP ownership in that same scope. Unowned, ambiguous, modified, or ownership-unsafe collisions are reported and preserved.

Reconciliation is ordered as inspect current and obsolete entries, classify the installation, project or repair the complete current family, verify that complete current family, and only then retire owned obsolete entries. A failure before current-family verification leaves obsolete entries in place. A retirement failure reports a partial migration with the exact surviving obsolete identity; it never rewrites the outcome as success or rolls back a verified current family by deleting native destinations directly.

Root `zpp init` remains first-install behavior for a truly empty selected agent, but recognizes an old-only user-scope installation as an explicit migration request and runs the shared reconciliation rather than layering a new family beside it. An agent with any current-family projection remains installed and is directed to root `zpp sync`. Root `zpp sync` reconciles current and obsolete user-scope entries even when only obsolete owned entries establish installation. `zpp workflow update` applies the same operation to exactly its selected user or project scope. `zpp workflow install` preflights both inventories and refuses an existing, obsolete, unmanaged, or conflicting destination before projecting anything, directing an owned existing installation to update or synchronization as appropriate. This prevents the observed prefix-install failure where a late `zpp-workflow` collision leaves only one new skill installed.

### Keep ZPP as the only installed tool

OpenSpec Bundler intentionally has no executable entry point. ZPP depends on it as a Python library and is the only package installed with `uv tool install`. The package metadata version, `zpp.__version__`, and `zpp --version` output form one release identity and must match exactly.

Distribution verification builds the ZPP wheel through the declared backend, installs that wheel into a disposable tool environment, observes the `zpp` executable and its matching version, and inspects that environment to prove Bundler is present only as a ZPP dependency. It must not attempt `uv tool install openspec-bundler`, require a Bundler console script, or report the dependency as a second installed tool.

### Move the shared behavior gate to the kernel

`zpps-workflow-kernel` becomes the only workflow-owned `zpp behave` gate identity because every governed playbook transition is assessed through it. Repository mappings using `zpp-workflow` must be updated explicitly; targeted verification does not alias or migrate the old gate and uses deterministic affected selection when the current gate is absent.

### Reconcile cross-capability operation authority

The hard cut applies to every current canonical capability, not only the workflow-family specification. Bundler acquisition is requested by the active complete playbook or a directly invoked mutating component through `zpps-workflow-kernel`; the removed monolithic identity owns no lease behavior. The packaged OpenSpec maintenance companion likewise names only the current ZPP-owned adapters for its bounded operations and never treats generated upstream `openspec-*` skills as operation authority. Historical tombstone inventories and rejection scenarios retain removed names only to describe detection, cleanup, and no-alias behavior.

### Verify executable package behavior without testing prompt policy

The established `features/consolidated_workflow_skill/` root owns executable packaged-family loading, ordering, adapter inventory, and contextual-trait inventory through the package public API. `features/openspec_skill_provisioning/` owns packaged projection and absence of generated skills. The product lifecycle root owns obsolete retirement and shared-inventory behavior; the duplicate obsolete-preservation example is removed from the provisioning root. `features/behavior_verification/` owns the public `zpp behave` gate-selection boundary and binds to the behavior-verification capability, while the consolidated-workflow requirement owns only the selected workflow identity and no-alias policy.

Playbook sequences and conditions, kernel assessment boundaries, subordinate authority limits, adapter stopping instructions, and stage conduct are agent prompt policy. They remain normative skill/specification responsibilities and are not represented as Behave scenarios or tests that assert packaged prose. Unit matrices are retained only for actual pure executable functions such as inventory ordering and tombstone classification. If a future route classifier, envelope validator, or binding parser becomes product code, its case matrix belongs in unit tests; prose alone does not justify such a function or test. Each executable capability root remains independently runnable with thin, scenario-selected bindings through a public product surface.

## Risks / Trade-offs

- [Complete playbooks repeat the ordered component-use skeleton] → Keep operation bodies in `zpps-*`, require every playbook to state its own sequence and conditions, and review each playbook independently rather than extracting a hidden shared sequence.
- [The installed skill count grows substantially] → Use precise descriptions and deterministic grouping so an invocation loads one complete playbook and only its currently used bounded components.
- [A directly invoked component may begin acting like another workflow authority] → Require complete bounded inputs and outputs, allow it to obtain only the guard needed for its selected operation, and review rejection of sequence selection, lease expansion, commits, and lifecycle continuation.
- [OpenSpec and feature files may drift after scenario transfer] → Use stable bidirectional bindings and require semantic duplicate, orphan, and target-resolution audits during shaping, specification formation, and verify-change.
- [A workflow family may install on a machine without a usable OpenSpec executable] → Keep lifecycle installation independent and let the invoked adapter report the exact missing or unsupported runtime interface without partial mutation.
- [Trait narrowing may remove useful ecosystem detail accidentally] → Move only invariant clauses, retain selected language/framework content, and verify the exact reduced family inventory and representative resolution.
- [Hard-cut projection may encounter user-created skills with obsolete names] → Remove only Agent Router-owned tombstones and preserve every unowned collision.
- [Installing the current family can fail after some current entries were projected] → Preflight install, reconcile migrations through one ordered operation, retain owned obsolete entries until the complete current family verifies, and report the exact partial state.
- [User- and project-scope ownership evidence can be confused] → Carry explicit scope and project root through current inspection, tombstone inspection, projection, verification, and retirement.
- [Package metadata and CLI version can drift] → Derive and test one release identity across package metadata, `zpp.__version__`, CLI output, and the built wheel.
- [Bundler may be mistaken for a separately installed tool] → Keep it library-only, install only the ZPP wheel as a tool, and verify the resulting environment exposes only the `zpp` console command from this dependency set.
- [Existing repositories may retain the old behavior gate] → Make the new gate explicit, use affected selection when absent, and provide no silent translation.

## Migration Plan

1. Add scenario-selected RED coverage only for executable package and lifecycle behavior in the capability-owned Behave roots, and add focused unit matrices only for existing or introduced pure functions.
2. Package the five complete Markdown playbooks, guard-only kernel, and substantive directly invokable phase and operation skills behind a deterministic family loader while the old projection remains unchanged.
3. Move invariant content into the owning skills, narrow retained traits, and remove the three obsolete trait families.
4. Package the eleven procedure-complete OpenSpec adapters, preserving each upstream operation's state discovery, ordered procedure, boundary, outputs, and failures under ZPP constraints; explicitly exclude onboarding, delete `zpp.utils.openspec` and generated-entry construction, and remove every OpenSpec process call from initialization, synchronization, and reset.
5. Add the canonical five-field OpenSpec-to-BDD declarations, transfer executable examples into capability feature roots, remove cross-root or OpenSpec acceptance duplicates, and enforce single acceptance authority before canonical synchronization.
6. Replace the shared lifecycle inventory, add ownership-safe tombstone retirement, and change the workflow behavior gate.
7. Remove the packaged `zpp-workflow` asset and generated-skill utilities after every caller uses the new family.
8. Reconcile the canonical capability purposes and requirements, including Bundler and maintenance operation authority, during specification formation, then run complete verification and a clean package build.
9. Replace command-local projection loops with the shared scope-aware current-plus-obsolete reconciliation operation, wire explicit old-only migration through init, sync, and same-scope workflow update, and make workflow install preflight conflicts before mutation.
10. Align package and runtime version sources, then verify a built ZPP wheel as the sole installed tool with OpenSpec Bundler present only as its library dependency.

Rollback requires restoring the prior package as one coherent version and synchronizing through Agent Router; the new and old workflow families are never projected together as a compatibility mode.
