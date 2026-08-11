## Context

ZPP already owns the repository trait and behavior-mapping schemas, while Agent Router owns native skill projection. Root initialization composes the packaged workflow skill and native hook with freshly generated OpenSpec operation skills. Confirmed reset preflights packaged assets and separately force-removes generated OpenSpec skills.

The missing layer is agent-facing authoring knowledge. The owner confirmed two small manual skills, automatic user-scope projection through root initialization, reset removal, no hook participation, no new CLI surface, and no BDD work for this change.

## Goals / Non-Goals

**Goals:**

- Package one focused skill for behavior mapping and one for trait family authoring.
- Teach repository-sensitive decisions and safety boundaries that schemas alone cannot express.
- Reconcile both skills through root initialization for every selected agent.
- Remove them through the same standard safety boundary as the packaged workflow skill.
- Keep current OpenSpec generation preflight and grouped workflow behavior intact.

**Non-Goals:**

- Add a configuration generator, provider adapter, hook, trait family, or CLI command.
- Run either skill automatically or make either part of the consolidated workflow.
- Force-remove modified or unmanaged packaged authoring skills.
- Add a behavior feature or `zpp.behave.yaml` to this repository for this change.
- Encode framework-specific commands that repository evidence must supply.

## Decisions

### Package two independent manual skills

`zpp-configure-behave` owns behavior-mapping authoring guidance and `zpp-author-trait` owns one-family TOML guidance. Each directory is initialized through the standard skill scaffold and contains one concise `SKILL.md` plus minimal `agents/openai.yaml` interface metadata. It contains no scripts, references, assets, or auxiliary documentation. This keeps each skill self-contained while ensuring that triggering one operation does not load the other domain.

A combined authoring guide was rejected because behavior segmentation and trait selection have different schemas, validation surfaces, and safety failures. Traits were rejected because authoring instructions are explicit agent operations rather than automatically injected repository environment policy.

### Reuse existing public commands

The behavior skill uses `zpp behave init` and `zpp behave COMMAND` after inspecting repository-owned commands. The trait skill uses `zpp trait init` and focused `zpp resolve --trait ... --explain`. Neither skill receives a new programmatic callback or internal API.

Deterministic generator scripts were rejected because the essential work is repository-dependent judgment, while ZPP's current schemas and commands already provide the low-freedom validation boundary.

### Load authoring assets before projection and project them after the native hook

The artifact layer exposes a deterministic detached tuple ordered as `zpp-configure-behave`, then `zpp-author-trait`. Initialization loads that tuple before entering generated OpenSpec preparation. Once every selected inventory validates, each agent receives workflow skill, native hook, both authoring skills, then generated operation skills.

Adding these skills to grouped workflow commands was rejected because they are general ZPP authoring operations, not the consolidated workflow integration. Adding another lifecycle command was rejected as unnecessary control-surface complexity.

### Apply standard reset safety

Reset inspects both authoring skills with the packaged workflow skill and hook before mutation, then removes present intact projections through ordinary Agent Router uninstallation. Modified or unmanaged authoring skills stop reset. Forced deletion remains exclusive to regenerated OpenSpec skills.

Treating the authoring skills as forced disposable output was rejected because they are static packaged assets and do not share the explicit regeneration/removal contract established for OpenSpec output.

### Verify without BDD

Focused artifact, CLI, reset, and end-to-end tests prove packaging, content markers, projection order, failure atomicity, standard removal, and repeated initialization. Strict OpenSpec validation and complete existing repository gates remain final requirements, but this change adds no Gherkin feature or behavior mapping.

## Risks / Trade-offs

- **A skill recommends an overly narrow segmentation** → Require conservative path coverage and preserve broad runtime fallback for shared or uncertain impact.
- **A skill invents executable syntax** → Require repository configuration or explicit owner choice and only supported explicit providers.
- **Installed packaged content is locally modified** → Agent Router's default ownership checks preserve it and reset fails closed.
- **More assets increase initialization and reset results** → Keep a fixed two-skill inventory and deterministic within-agent order.
- **Guidance drifts from schemas** → Assert key content and commands in artifact tests and maintain the skills with the canonical capability specs.

## Migration Plan

1. Ship both skills in the ZPP package and extend root initialization and reset together.
2. Existing users rerun `zpp init --agent ...` to receive the authoring skills.
3. Rollback removes the two projections from init/reset composition; existing Agent Router-owned copies can be removed by confirmed reset before rollback or by normal Agent Router lifecycle.

## Open Questions

None.
