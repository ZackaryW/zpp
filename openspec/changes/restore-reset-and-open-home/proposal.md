## Why

ZPP 2.0 omitted the confirmed reset boundary while retaining mutable OpenLease state and user-scope Agent Router projections, leaving no single ownership-safe recovery operation. Its default state path also exposes OpenLease as the product home, so users cannot open one stable `.zpp` home for inspection and manual handling.

## What Changes

- Restore root `zpp reset --yes` as a complete all-agent user-scope cleanup followed by replacement of only the selected ZPP home's `openlease` state.
- Require complete Agent Router preflight before reset mutation, remove only intact ZPP-owned user workflow skills and hooks, and leave conflicts visible without direct native deletion.
- Add root `zpp open` to create the selected ZPP home when absent and launch it through the platform's native folder opener without interpreting its contents.
- Make `~/.zpp` the default ZPP home and place OpenLease state under `<home>/openlease`; root `--path` selects an alternate ZPP home for both commands and other OpenLease-backed operations.
- Preserve repository `.zpp` documents, `zpp.behave.yaml`, project-scope projections, plugins, external worktrees, and unrelated agent assets across reset.
- Keep the former global authored-trait collection and `--overwrite-global-traits` option removed.
- **BREAKING** relative to the incomplete ZPP 2.0 preview: the default OpenLease state moves from `~/.openlease` to `~/.zpp/openlease`, and `--path` identifies the ZPP home rather than the OpenLease state directory itself.

## Capabilities

### New Capabilities

- `product-home-lifecycle`: Defines ZPP home selection, native folder opening, confirmed state replacement, all-agent reset preflight, and reset ownership exclusions.

### Modified Capabilities

- `repository-trait-bootstrap`: Adds root `open` and `reset` to the stable command hierarchy and routes OpenLease-backed operations through the selected home's `openlease` child.
- `automatic-trait-hooks`: Adds ownership-safe removal of every supported agent's user-scope ZPP workflow hook during confirmed reset without broadening ordinary workflow removal.

## Impact

- Public CLI: root `open` and `reset --yes` return; root `--path` now selects a ZPP home.
- Filesystem: the default managed OpenLease state becomes `~/.zpp/openlease`; explicit opening may create only the selected home directory.
- Agent integration: reset inspects and removes current `zpp-workflow` skills and `zpp-session` hooks in user scope through Agent Router.
- Runtime utilities: platform folder opening, destructive-path validation, staged state replacement, and complete preflight reporting require focused adapters and tests.
- Documentation and packaging: README command and state-path guidance must describe the restored lifecycle.

## Unresolved — Do Not Assume

None.
