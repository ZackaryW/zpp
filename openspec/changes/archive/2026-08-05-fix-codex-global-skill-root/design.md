## Context

See `proposal.md` for motivation. The projection resolver currently assigns one relative Codex workflow root, `.agents/skills`, to both scopes. OpenSpec-generated Codex skills already use `.codex/skills`, and the ownership model supports multiple disjoint manifests in one directory, as demonstrated by the existing shared Pi and Claude roots.

The current official Codex manual documents `~/.agents/skills` for personal skills, but the owner verified that the affected Codex installation on macOS loads the required user-global bundle from `~/.codex/skills`. The owner's Windows environment independently consumes generated OpenSpec skills from `.codex/skills`. The product must honor that explicit cross-platform runtime compatibility correction while retaining `.agents/skills` for repository-local distribution.

## Goals / Non-Goals

**Goals:**

- Resolve the Codex workflow root by scope and the active platform-native user home.
- Co-locate global ZPP workflow and generated OpenSpec skills without merging their ownership.
- Keep all lifecycle and top-level discovery operations on the same corrected projection mapping.

**Non-Goals:**

- Change Pi or Claude destinations.
- Change Codex's repository-local `.agents/skills` convention.
- Delete, relocate, or otherwise mutate historical user content under `~/.agents/skills`.
- Add a second global copy or duplicate skill names across both roots.

## Decisions

### Make Codex workflow projection scope-aware

The workflow projection resolver will choose `.codex/skills` beneath its supplied home only when `scope == "global"`; local resolution will continue to choose `.agents/skills` beneath the selected repository target. Every existing lifecycle consumer and top-level update already goes through this resolver, keeping the fix centralized and platform agnostic.

Alternative considered: change Codex to `.codex/skills` in both scopes. This would contradict the retained repository convention and widen the owner's global-only correction.

Alternative considered: branch the global destination by operating system. Both observed environments recognize `.codex/skills`, so a platform branch would add policy without improving compatibility.

### Reuse independent manifests in the shared global root

The ZPP bundle owns `zpp-*` directories and `.zpp-workflow-skills.json`; OpenSpec owns `openspec-*` directories and `.zpp-openspec-skills.json`. Existing mutation merging accepts shared parent directories and rejects duplicate owned paths, so no new coexistence abstraction is needed.

Alternative considered: keep OpenSpec and ZPP in separate roots. That preserves the failing split and does not satisfy the corrected global destination.

### Do not automatically migrate the historical root

The corrected installer will create and manage the new global projection when the owner reruns global workflow install. Historical `~/.agents/skills` content remains untouched because the request does not authorize deleting or moving that user directory and official Codex documentation still recognizes it as a valid personal-skill location.

## Risks / Trade-offs

- [Both old and new roots contain the same ZPP skill names] -> Do not create a second projection automatically through top-level update; document rerunning explicit global install and leave historical cleanup under owner control.
- [Two ownership manifests share `.codex/skills`] -> Retain disjoint path ownership and cover install, update, remove, and OpenSpec preservation in BDD.
- [Future Codex versions standardize one global root] -> Keep the adapter scope mapping focused so a later compatibility correction remains localized.

## Migration Plan

1. Upgrade ZPP with the corrected adapter.
2. Run `zpp workflow install --agent codex` to install the bundle under `~/.codex/skills`.
3. Verify Codex discovers the new projection.
4. Leave the historical `~/.agents/skills` projection untouched unless the owner separately chooses to remove it.

Rollback restores the earlier global mapping; the `.codex/skills` projection remains manifest-owned and can be removed explicitly with the corrected version before rollback if desired.
