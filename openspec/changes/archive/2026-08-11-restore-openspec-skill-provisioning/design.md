## Context

The consolidated `zpp-workflow` skill delegates specification operations to six OpenSpec-owned skills, but ZPP 2.0 initialization projected only the workflow skill and native hook. OpenSpec owns generation, Agent Router owns native destinations, and confirmed reset coordinates Agent Router cleanup with OpenLease state replacement.

The owner corrected the initial complete-lifecycle proposal: OpenSpec generation belongs only to root initialization, grouped workflow lifecycle commands remain small, and reset discards generated skills through explicit no-history forced owned deletion rather than introducing update controls.

## Goals / Non-Goals

**Goals:**

- Make successful `zpp init` immediately ready for delegated OpenSpec operations.
- Generate every selected agent inventory before any projection starts.
- Reconcile generator changes through deterministic provenance and repeated initialization.
- Force-remove proven-owned generated skills during reset without invoking OpenSpec.
- Preserve Agent Router and OpenLease ownership boundaries.

**Non-Goals:**

- Installing or updating the OpenSpec executable.
- Bundling generated snapshots.
- Adding `--with-openspec`, an OpenSpec update command, or generated-skill controls to `zpp workflow`.
- Direct native destination mutation or retained force-removal history.

## Decisions

### Generate from the installed OpenSpec CLI

ZPP detects `openspec --version`, runs `openspec init . --tools AGENT --force` in one disposable repository per selected agent, and requires the exact six canonical names at that agent's native generated root. It adds deterministic ZPP/OpenSpec-version provenance before loading each Agent Router `Skill`.

Bundled snapshots and reproduced template logic were rejected because OpenSpec owns generation and installed versions can evolve.

### Hold all generated sources through one initialization context

One `ExitStack` enters every selected generator in first-seen order and yields only after every inventory validates. Root initialization then projects the workflow skill, native hook, and six generated skills per agent while every temporary source remains alive.

Generating and projecting one agent at a time was rejected because later generation failure would create avoidable partial multi-agent initialization.

### Keep generation init-only

Root `init` freshly regenerates on every invocation and uses Agent Router's safe user-scope install reconciliation. `workflow install|update|remove` retains its existing skill-and-hook behavior and exposes no OpenSpec option.

A separate update surface and automatic OpenSpec participation in grouped workflow lifecycle were rejected as unnecessary human-facing complexity.

### Force-remove canonical skills during reset

Reset retains complete read-only preflight for every supported agent's `zpp-session` hook and `zpp-workflow` skill. After that preflight and OpenLease replacement preparation succeed, runtime removal calls Agent Router `uninstall_skill(force=True)` for each canonical OpenSpec name.

Agent Router requires valid matching ownership, removes modified content and ownership without retained history, treats wholly absent state as converged, and refuses unmanaged or invalid ownership. Failures are aggregated, prior OpenLease state remains unchanged, and earlier removals remain retryable.

Regeneration during deletion and an inspect-by-name API were rejected in favor of explicit forced deletion.

### Pin the component contract

ZPP pins Agent Router `0.1.3` at `9c7984f25c1809a4a9245a746d0c741e3e3eb180`. Its adapter forwards force without interpreting ownership or destinations.

## Risks / Trade-offs

- **OpenSpec is unavailable or changes inventory** → Initialization fails before selected projection.
- **Projection fails after generation preflight** → Agent Router reports the conflict; ZPP has no adoption fallback.
- **Forced cleanup encounters unmanaged content** → Agent Router preserves it and reset preserves prior OpenLease state.
- **Runtime removal fails after earlier removals** → Failures are aggregated and retry converges; cross-agent deletion is not presented as transactional.
- **Temporary sources disappear early** → One shared context encloses all projection and focused tests enforce lifetime.

## Migration Plan

1. Publish Agent Router 0.1.3 and pin ZPP to it.
2. Ship init-time generation and reset-time force cleanup together.
3. Existing users rerun `zpp init --agent ...` to obtain generated operation skills.
4. Rollback restores the earlier dependency pin and removes generated-skill init/reset composition; projected skills remain Agent Router-owned.

## Open Questions

None.
