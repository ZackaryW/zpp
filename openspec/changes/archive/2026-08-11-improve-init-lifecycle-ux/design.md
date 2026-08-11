## Context

`zpp init` and `zpp reset --yes` currently serialize complete lifecycle structures for every operation. This is useful for automation but unsuitable as the default terminal result. Initialization already regenerates every source before projection, while Agent Router decides whether each destination is absent, current, outdated, owned-but-diverged, or conflicting.

## Goals / Non-Goals

**Goals:** Make normal lifecycle output one concise line, preserve deterministic details behind `--json`, and let `zpp init --force` reproject every selected integration through Agent Router.

**Non-Goals:** Add a general output framework, broaden grouped `zpp workflow` behavior, adopt unmanaged destinations, bypass hook safety, or write native agent files directly.

## Decisions

Add command-local `--json` flags to root initialization and reset. The default renderer will aggregate lifecycle statuses in deterministic human terms such as installed, updated, unchanged, removed, and already absent. JSON mode will retain the existing complete report shapes for automation.

Forced initialization will retain complete source generation and validation before any projection. It will request forced replacement for safely owned skill destinations and reproject hooks through Agent Router's public hook lifecycle. Current or absent assets remain eligible; unmanaged, mismatched-ownership, or unsafe shared-hook conflicts remain errors. This preserves component authority while making owned skill drift recoverable.

Keep summary calculation separate from lifecycle decisions. Rendering consumes completed result dictionaries and never changes success, failure, ordering, or mutation behavior.

## Risks / Trade-offs

- **Human output hides individual details** → Preserve the complete deterministic report behind `--json`.
- **Force could overwrite unrelated files** → Use only Agent Router public ownership-aware operations and preserve conflicts for unmanaged or mismatched destinations.
- **Remove-and-reproject can partially fail** → Prepare every generated source first and keep Agent Router failures visible; never claim summary success after an exception.
