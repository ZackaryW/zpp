---
name: zpp-author-skill
description: Create or revise focused ZPP workflow skills with durable context and explicit control flow. Use when authoring stage-specific skills, extracting repeated workflow policy into traits, or correcting skill boundaries, pause conditions, authority, and handoffs.
---

# Author a ZPP skill

Keep a skill stage-specific and procedural. Move concise cross-cutting advisory
direction into traits; move platform, framework, runner, and tool-selection
policy into independently activatable traits. Never duplicate canonical
OpenSpec product behavior in a skill.

1. Establish concrete triggers, owned inputs, outputs, mutations, verification,
   and handoff before writing instructions.
2. Record durable progress before absorbing additional information, then revise
   that record as new evidence changes it. For the complete pattern, read
   [context-continuity.md](references/context-continuity.md).
3. Define automatic continuation, human gates, fallback ownership, and failure
   behavior explicitly. Read
   [explicit-control-flow.md](references/explicit-control-flow.md).
4. Keep the body concise, imperative, and platform-neutral. Put focused detail
   in directly linked references and deterministic repeated operations in
   scripts.
5. Preserve authority boundaries: system, developer, user, canonical OpenSpec,
   active changes, and owning workflow stages remain authoritative in that
   order. A skill may direct work only within granted authority.
6. Validate the finished folder and test the behavior through its real workflow
   surface. Do not let a supporting agent own root RED/GREEN verification or a
   commit.
