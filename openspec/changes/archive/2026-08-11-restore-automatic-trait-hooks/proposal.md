## Why

ZPP 2.0 currently packages trait resolution as an instruction inside the workflow skill, so agents receive environment behavior only if they correctly follow a manual `zpp resolve` bootstrap step. ZPP is intended to install agent-native hooks that resolve and inject traits automatically; the skill should govern workflow stages, not bootstrap its own runtime context.

## What Changes

- Remove the non-runtime `REFERENCE_BEHAVIOR.md` audit document from shipped artifacts.
- Package one native automatic trait-context hook per supported Agent Router agent.
- Make root `init` and `workflow install|update|remove` project the consolidated skill and the selected agent's hook through Agent Router.
- Have each hook invoke ZPP trait resolution for the current repository at the earliest native context-injection event and inject only complete rendered trait bodies.
- Remove instructions to run `zpp resolve`, manage `ZPP_CONTEXT`, or bootstrap trait context from the consolidated workflow skill.
- Keep the workflow skill responsible for explicit stage dispatch, authority, gates, and completion while treating already-injected trait bodies as advisory environment policy.
- Preserve `zpp resolve` as the public read-only resolution and explanation surface rather than introducing a second trait engine for hooks.
- Add family-level `automatic`, `manual`, and `always-run` activation modes. Automatic families use normal facet/evidence activation in common resolution; manual families appear only when named directly by `resolve`; always-run families join common resolution while bypassing facet/evidence activation.
- Add a repeatable direct family query to `resolve` so a caller can request one or more manual families explicitly without activating every manual family.
- Preserve each family's selection policy after activation candidates are formed, including for always-run families; bypassing activation does not bypass `first-win`, `all`, or `extend` retention.
- Surface hook resolution failures without injecting stale or partial trait bodies and without granting the hook workflow authority.
- Resolve plugin traits only from the invoking Agent Router `Agent` context. Construct Agent Router with the real user home and the selected repository as `project_root`, so user and project plugin state use the router's current home-rooted state contract.
- Use Agent Router's explicit project `update_skill` operation for project-scoped workflow updates; retain ownership-safe `install_skill` reconciliation for user-scoped maintenance and Agent Router-owned hook lifecycle operations.

## Capabilities

### New Capabilities

- `automatic-trait-hooks`: Defines agent-native hook packaging, automatic repository trait resolution and context injection, failure behavior, and Agent Router-owned projection.

### Modified Capabilities

- `consolidated-workflow-skill`: Removes runtime resolution/bootstrap instructions from the skill and narrows it to workflow authority over already-injected advisory traits.
- `repository-trait-bootstrap`: Changes workflow lifecycle commands and root initialization from skill-only projection to coordinated skill-and-hook projection through Agent Router.
- `toml-trait-catalog`: Adds explicit family-level activation metadata for automatic, manual, and always-run traits.
- `trait-resolution`: Adds manual family queries, always-run candidate behavior, and a prompt-ready rendered output contract for automatic hooks while preserving deterministic explanation and explicit session-context data.

## Impact

- Affects packaged assets under `zpp.artifacts`, Agent Router adapters, workflow lifecycle commands, root initialization, resolution rendering, and per-agent integration tests.
- Adds Agent Router `Hook` projection to the existing `Skill` lifecycle without adding a ZPP-owned destination writer.
- Updates the Agent Router dependency to the current owner-provided revision and consumes its home-rooted state and explicit project skill-update contracts directly.
- Restores invoking-agent plugin traits through Agent Router's active `zpp.traits` artifact statuses; ZPP does not combine plugin contexts from several agents.
- Does not restore ZPP 1.x skill or hook migration, OpenLease spaces, guard behavior, or compatibility-owned agent discovery.
- Removes `src/zpp/artifacts/REFERENCE_BEHAVIOR.md`; reference coverage remains proven by executable asset tests rather than shipped prose.

## Unresolved — Do Not Assume

None. The owner confirmed that `[meta].activation` defaults to `automatic`; a repeatable `resolve --trait <family>` query limits output to the named families and permits a manual family to use its normal facet/evidence matching; an `always-run` family bypasses facet/evidence activation during unfiltered common resolution but still applies its declared `first-win`, `all`, or `extend` retention policy.
