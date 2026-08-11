## Context

The first ZPP 2.0 implementation correctly separated workflow policy into one skill and environment policy into TOML traits, but it made the skill responsible for running `zpp resolve`. That leaves trait activation dependent on an agent following bootstrap prose and gives the skill two unrelated jobs. Agent Router already owns supported-agent destinations, plugin state, skills, and native hooks, and its current revision distinguishes explicit project skill replacement from ownership-safe user installation.

The correction spans packaged artifacts, trait metadata and resolution, CLI rendering, Agent Router construction, and lifecycle orchestration. Hooks must work for Codex, Claude Code, Pi, and Kimi without restoring ZPP 1.x guard, migration, or destination-writing behavior.

## Goals / Non-Goals

**Goals:**

- Install one workflow skill and one native automatic trait hook for each selected agent.
- Keep the skill limited to workflow stages, gates, authority, and handoffs.
- Make unfiltered resolution suitable for direct prompt injection while preserving structured explanations.
- Add deterministic `automatic`, `manual`, and `always-run` family activation.
- Restore invoking-agent plugin trait discovery under Agent Router's home-rooted state model.
- Use Agent Router's current project update semantics without ZPP-owned destination mutation.

**Non-Goals:**

- Restoring ZPP 1.x hooks, guards, predecessor migration, stage skills, or OpenLease spaces.
- Making hooks workflow authorities or stage dispatchers.
- Adding hidden session caches or attempting to mutate a parent process environment.
- Combining plugin state from multiple agent identities during one resolution.

## Decisions

### Native hooks own automatic trait injection

ZPP packages a native hook for each Agent Router `Agent`. Codex and Claude Code use their native JSON session-start form, Kimi uses its TOML session-start form, and Pi uses a TypeScript `before_agent_start` extension that appends resolver output to the system prompt. Each hook invokes the public command `zpp resolve --agent <agent> .` at the earliest supported context-injection event.

This keeps one resolution engine and lets Agent Router own destination formats and lifecycle. A generic instruction in the skill was rejected because compliance is neither automatic nor reliably observable.

### Resolution has a prompt surface and a diagnostic surface

Successful `zpp resolve` without `--explain` writes only retained complete bodies in deterministic resolution order, separated so the output can be injected as prompt context without parsing a transport envelope. An empty resolution writes no trait content. `--explain` emits the structured diagnostic envelope, including bodies, effective context, and decisions.

Hooks pass resolver stdout only after a successful process result. A resolver or hook failure remains visible and contributes no partial or remembered body output. Incoming compatible `ZPP_CONTEXT` remains an input to resolution and the diagnostic result can expose the newly computed value, but hooks do not promise to publish child-process environment changes into their parent sessions.

### Activation precedes the existing selection policy

Each one-family TOML document accepts `[meta].activation` with values `automatic`, `manual`, or `always-run`; omission means `automatic`. The highest-precedence contributing document supplies the effective activation alongside selection.

Unfiltered resolution excludes manual families. Automatic families form candidates using the existing facet/evidence rules. Always-run families treat every effective flavor as an activation candidate without evaluating facet or workspace evidence, then apply the effective `first-win`, `all`, or `extend` selection policy normally. Facets from bypass-selected always-run flavors are not evidence-derived and therefore do not backfill context.

A repeatable `--trait <family>` filter limits resolution to exactly the named families. This makes manual families eligible, but does not make their flavors unconditional: manual and automatic families still use normal facet/evidence activation. Named always-run families retain always-run semantics. An unknown requested family is a user-visible error.

Family filtering rather than a second manual command was selected because it preserves one public resolution contract and supports requesting several related policies at once.

### Agent Router receives real home and project context

ZPP constructs each `AgentRouter` with `home=Path.home()` and `AgentEnvironment(Path.home(), selected_repository)`. Only the router for the `--agent` value contributes active `zpp.traits` plugin artifacts. This follows Agent Router's current home-rooted state and prevents a repository path from masquerading as the user home.

Project `workflow update` calls `update_skill` for the exact selected project root. Project install and user install/update call `install_skill`; hook install/update uses `install_hook`; removal uses the corresponding uninstall operations. ZPP supplies packaged `Skill` and `Hook` assets but never writes native destinations itself.

### Workflow lifecycle treats skill and hook as one requested integration

Root `init` and grouped workflow lifecycle commands operate on both assets for every selected agent, retaining first-seen agent order. Results identify both asset operations. Component rejections remain visible; ZPP does not fall back to its own writer. The lifecycle does not imply that uninstalling one scope removes another scope's asset.

### Audit prose is not a runtime artifact

`src/zpp/artifacts/REFERENCE_BEHAVIOR.md` is removed. Reauthored behavior remains in `artifacts/traits`, while executable asset and feature tests prove coverage. Shipping a second prose inventory creates ambiguous authority without affecting runtime behavior.

## Risks / Trade-offs

- **[Native agent formats evolve]** → Keep hook payloads as packaged assets covered by exact projection tests and let Agent Router own destination adaptation.
- **[A paired lifecycle can partially succeed if the second router mutation fails]** → Validate packaged assets and router inputs before mutation, report each completed result truthfully, and never attempt an unsafe compensating overwrite.
- **[Prompt-ready output is less machine descriptive]** → Preserve complete machine diagnostics behind `--explain`.
- **[Always-run bypass can select broad content]** → Keep it explicit at family metadata and still apply the declared selection policy.
- **[Project update intentionally replaces selected local skill content]** → Use `update_skill` only for explicit project `workflow update`; user maintenance remains ownership-safe `install_skill`.

## Migration Plan

1. Update Agent Router to the owner-confirmed revision and adapt router construction.
2. Add activation parsing and resolution behavior, then change CLI rendering and family filters.
3. Package and test four native hooks.
4. Coordinate skill-and-hook lifecycle in root initialization and workflow commands.
5. Remove resolver bootstrap prose from the workflow skill and delete the audit artifact.
6. Verify unit, BDD, CLI, packaged-asset, and clean-build behavior before archiving this correction.

Rollback is a source rollback of this change. ZPP does not migrate or delete unmanaged legacy assets as part of either direction.

## Open Questions

None.
