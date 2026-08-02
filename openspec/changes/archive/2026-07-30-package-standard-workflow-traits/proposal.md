## Why

The permanent workflow skills repeat cross-cutting directions, causing policy drift and making stage-specific skills larger than their actual responsibilities. ZPP needs a standard trait layer for shared advisory governance while skills retain focused operational gates and owning skills retain non-bypassable rules.

## What Changes

- Expand the concept of ZPP's standard workflow from seven permanent skills to a coordinated package of permanent skills and compact standard traits.
- Move genuinely cross-cutting advisory directions out of repeated skill sections and into independently configurable traits.
- Keep stage-specific inputs, actions, gates, and verification responsibilities in their owning skills.
- Keep zmem checkpoint worthiness centralized in `zpp-commit-zmem`; other skills SHALL NOT restate or negate that decision contract.
- Keep non-bypassable safety, mutation-authority, and operation-ownership constraints in enforceable skills or product utilities rather than making them optional advisory text.
- Provide an automatic-workflow trait activated through `trait.json`, configured for automatic progression by default, and locally overrideable through `.zpp/config.json` to use manual progression; either mode preserves passive skill lookup and cannot execute skills, bypass failed gates, settle missing decisions, or grant authority.
- Make automatic progression continue an explicitly delegated change across ordinary completed workflow stages without requesting approval at each handoff. Pause only for unresolved clarification, a newly discovered product boundary, or a missing or changed utility shape; an explicit end-to-end delegation overrides a manual stage pause for that delegated change.
- Package `automatic-workflow`, `zero-assumptions`, and `ponytail` as the initially activated platform-neutral base traits.
- Package `python-bdd`, `python-tdd`, and `python-build` as independent optional Python traits covering Behave, pytest, and uv environment guidance respectively; do not activate them in the platform-neutral default trigger configuration.
- Allow standard traits to carry default frontmatter configuration and participate in the existing `traitsConfig` overlay behavior so profiles and later layers can customize accepted advisory settings.
- Store required standard traits in a permanently present, user-owned `default` base profile under the existing profiles namespace and guarantee that profile is available to resolution before duplicated advisory sections are removed from distributed skills.
- Make profile activation an explicit persistent operation: `zpp global activate NAME` archives the current user-owned global layer as a collision-safe `{YYYYMMDD-HHMMSS}-global` profile, copies the selected user-owned profile into global, and preserves the selected profile for reuse.
- Add `zpp profile copy SOURCE DESTINATION` so users can derive profiles without activating or mutating the source.
- Keep `ZPP_PROFILE` as a temporary, non-mutating session override distinct from persistent global activation.
- Keep application-platform, framework, and test-runner guidance in independent optional traits rather than permanent workflow skills.

## Capabilities

### New Capabilities

- `standard-workflow-traits`: Package, activate, configure, and lifecycle-manage ZPP's standard advisory workflow traits without weakening skill-owned enforcement.

### Modified Capabilities

- `global-bootstrap-and-agent-setup`: Initialize and preserve the permanent user-owned default profile alongside neutral global state.
- `profile-and-saved-lifecycle`: Recognize the permanent default in named-profile listing and removal semantics without coupling it to saved overrides.
- `workflow-skill-distribution`: Manage one standard workflow composed of permanent skills plus standard traits and remove advisory duplication from skill bodies only after trait availability is guaranteed.
- `trait-resolution`: Include the accepted standard-trait source in deterministic layer composition and preserve existing authored replacement and `traitsConfig` override behavior.

## Impact

- Standard workflow artifact packaging, default-profile ownership, and lifecycle metadata.
- `zpp workflow install`, `update`, and `remove` lifecycle behavior.
- Trait activation, resolution precedence, configuration overlays, and removal behavior.
- Permanent `zpp-*` skill bodies and the automatic-workflow trait.
- Persistent global activation, temporary profile overrides, profile copying, and saved, repository, and subfolder override compatibility.
- No platform- or framework-specific policy will be embedded in permanent workflow skills or the initially activated platform-neutral base; concrete Python guidance will remain isolated in separately selectable traits.

## Established Boundaries

- A trait remains one UTF-8 Markdown file with YAML frontmatter and an advisory body; `trait.json` exclusively owns activation.
- Standard cross-cutting traits should remain small, layered directions rather than becoming one oversized governance document.
- Standard workflow traits belong to a `default` base profile inside the profiles namespace rather than an opaque additional layer.
- The `default` profile is an invariant of initialized ZPP state: initialization creates it, activation and copying never consume it, and profile or workflow lifecycle operations never remove or rename it.
- Global is the active user-owned configuration; named profiles are reusable user-owned configurations.
- `zpp global activate NAME` must preserve the current global as a `{YYYYMMDD-HHMMSS}-global` profile and copy, not consume, the selected named profile.
- Persistent activation must be atomic, collision-safe, and invalidate or rebuild affected caches without transferring cache or modification-sidecar state as authored profile content.
- `zpp profile copy SOURCE DESTINATION` must copy authored profile content without activating it or mutating the source.
- `ZPP_PROFILE` remains a temporary, non-mutating session override and must not perform the persistent activation transaction.
- Traits are advisory and cannot grant Git, destructive, external-mutation, or verification authority.
- `skill_lookup` remains passive metadata.
- Profiles and later participating layers must remain able to override accepted trait configuration through `traitsConfig`.
- `trait.json` exclusively activates `automatic-workflow`. Its frontmatter configuration uses `mode: automatic` by default, while a participating local `.zpp/config.json` may set `traitsConfig.automatic-workflow.mode` to `manual`; configuration does not activate or deactivate the trait.
- Permanent ZPP workflow skills must hand completed stages to the next owning skill automatically when automatic progression or explicit end-to-end delegation applies. A checkpoint, successful verification result, or ordinary stage transition is not itself a human gate.
- Automatic progression pauses only when outcome-changing clarification remains unresolved, implementation discovers a new product boundary, or the approved utility shape is missing or must change. Manual mode may request a stage handoff unless the user explicitly delegated the change end to end.
- Every standard advisory trait is configurable and disableable through `traitsConfig`.
- The user-owned `default` profile may be edited directly.
- `workflow remove` is limited to selected managed agent projections and never removes a profile or authored trait content.
- `zpp init` creates the bundled `default` profile only when it is absent and preserves an existing default byte-for-byte. Empty or cancelled agent selection affects only agent setup and never suppresses required user-state initialization.
- `workflow install`, `update`, and `remove` never mutate a profile. Updating or importing a newer bundled default into an existing user-owned default is outside this change.
- The initially activated platform-neutral trait set is `automatic-workflow`, `zero-assumptions`, and `ponytail`.
- Optional Python guidance is divided by responsibility: `python-bdd` covers Behave, `python-tdd` covers pytest, and `python-build` covers the uv environment. These traits are independently selectable and not activated by the platform-neutral default trigger configuration.
- Missing zmem is not a failed gate when no material tracked work exists.

## Explicitly Deferred

- An explicit refresh/import operation for applying a newer bundled default to an existing user-owned `default` profile.
- TypeScript-specific traits.
- Flutter-specific traits.

## Unresolved — Do Not Assume

None.
