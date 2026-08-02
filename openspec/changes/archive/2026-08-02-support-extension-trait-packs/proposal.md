## Why

ZPP is the sole trait resolver and profile owner, but extension plugins currently have no supported way to supply optional trait sources without manual file copying or becoming a second resolver. The governance plugin cleanup also exposes generic TypeScript, Flutter, and Python-Django guidance that belongs with ZPP rather than inside a Pathverse-specific plugin.

## What Changes

- Automatically discover trait sources from actively installed plugins in Codex, Claude, and Pi through expanded agent-specific installation utilities, without copying those sources into ZPP-managed profiles.
- Pass the invoking agent identity through each native ZPP session integration and discover only that agent's active plugin set through its authoritative installed-state contract; do not union other editors or treat marketplace caches, orphaned versions, disabled packages, or merely available plugins as active.
- Recognize a plugin-owned read-only trait source by its conventional `trait.json` and `traits/*.md` authored shape. Definitions omitted from `trait.json` remain available for later manual activation, while included fixed trigger rules participate automatically.
- Compose active plugin sources before global, selected profile, saved, and repository layers so every user-owned layer retains ordinary replacement, configuration-overlay, and trigger-overwrite control.
- Keep compiled external-source state in ZPP's independent cache namespace. Re-evaluate active identities, resolved roots, versions, and source freshness so disabling, updating, or uninstalling a plugin cannot leave stale traits participating.
- Preserve direct `zpp resolve` compatibility: without `--agent` it resolves no plugin sources, while native agent hooks always pass their explicit agent identity.
- Order distinct active plugin sources by stable plugin identity, deduplicate byte-identical trait definitions, and fail rather than silently override when different plugin sources define the same trait name with different content.
- Preserve the authored Markdown, `trait.json` activation ownership, profile overlays, and source-authoritative cache behavior already established for traits.
- Add `typescript-bdd`, `typescript-tdd`, `flutter-bdd`, `flutter-tdd`, and `python-django-tdd` as packaged optional ZPP traits that remain manually activated alongside the existing manual Python workflow traits.
- Teach the complete zmem tool through a `use-zmem` trait selected by `which: zmem`, a `zpp-use-zmem` skill covering the complete supported read surface, and the existing `zpp-commit-zmem` write/checkpoint skill referenced through trait skill lookup.
- Adopt a generic `zpp-lean-audit` skill with a direct, substantial grounding in the Ponytail project while preserving the utility workflow's maturity-and-proportional-coverage evaluation of third-party packages.
- Distill qualifying constitution directions into a `zpp-author-skill` skill with `references/context-continuity.md` and `references/explicit-control-flow.md`, not runtime traits.
- Replace the retired preferred-tooling monolith with focused `use-rg` and `use-jq` traits selected by `trait.json` rules using `which: rg` and `which: jq`; an unavailable executable leaves its trait inactive and never blocks work.
- Allow a Pathverse-specific plugin source to remain separately owned and automatically discoverable from its active editor installation without making that plugin a resolver or bootstrap-hook owner.

## Capabilities

### New Capabilities

- `extension-trait-packs`: Active editor-plugin discovery, external trait-source validation, deduplication, precedence, and integration with ordinary ZPP resolution.

### Modified Capabilities

- `standard-workflow-traits`: Add generic inactive TypeScript, Flutter, and Python-Django workflow traits distilled from the retired plugin supplementary guidance.
- `workflow-skill-distribution`: Add the confirmed generic tool-use and Ponytail audit skills transferred from the governance plugin without leaking platform policy into workflow-stage skills.
- `trait-resolution`: Compose validated active-plugin sources before user-owned layers while preserving user override authority.
- `global-bootstrap-and-agent-setup`: Pass the invoking Codex, Claude, or Pi identity into resolution from native global session integration.

## Impact

Affected surfaces include Codex, Claude, and Pi plugin-installation adapters, native hook context, external source validation, pack identity, packaged default trait definitions, the permanent/generic skill bundle, caches and sidecars, CLI tests, and the related governance-plugin change `retire-zpp-superseded-plugin-workflow`.

## Unresolved — Do Not Assume

- None.
