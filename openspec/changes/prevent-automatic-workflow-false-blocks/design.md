## Context

See `proposal.md` for motivation. Bundler intentionally accepts only paths beneath registered `openspec/` roots, while ZPP's kernel currently reports a component's complete changed-path inventory directly to that API. Separately, the decomposed workflow moved ordered sequencing from a kernel dispatcher into complete Markdown playbooks and intentionally left prompt policy without executable routing tests. The playbooks name Ponytail, but neither handoff nor wiring eligibility currently requires an observed Ponytail result.

## Goals / Non-Goals

**Goals:**

- Keep Bundler's OpenSpec authority boundary strict while preventing repository-local product files from becoming false lease violations.
- Preserve complete changed-path reporting by components and centralize classification in ZPP's Python runtime.
- Make Ponytail completion or skip explicit predecessor evidence for wiring after `zpp-auto` handoff.
- Add structural validation for the current playbook family without restoring stage selection to the kernel.

**Non-Goals:**

- Broaden Bundler leases to application, feature, or test files.
- Ignore paths outside registered repositories or OpenSpec paths owned by unheld stores.
- Add persisted workflow state, a monolithic stage dispatcher, or compatibility for the superseded `route-workflow-playbooks` design.
- Infer utility applicability in `zpp-auto` or the kernel.

## Decisions

### Classify paths in the ZPP adapter before Bundler audit

`BundlerLeaseService` will own a ZPP result containing `audited`, `ignored`, and `violations`. It will resolve registered store roots most-specific-first, classify paths outside all roots as violations, classify paths inside a registered root but outside its `openspec/` subtree as ignored, and forward the remaining OpenSpec paths to `LeaseCoordinator.audit`. Bundler remains unchanged and authoritative for held-store validation.

Filtering in the kernel skill was rejected because every agent would have to reproduce filesystem and nested-store logic. Changing Bundler was rejected because its package contract is explicitly OpenSpec-only.

### Keep the CLI backward-readable while exposing ignored paths

`zpp lease audit` will retain `ok`, `accepted`, and `violations`, with `accepted` representing Bundler-audited OpenSpec paths, and add `ignored` for repository-local paths outside lease scope. Existing consumers that read the original fields continue to work, while workflow assessment gains explicit evidence that a path was classified rather than lost.

### Require a real Ponytail receipt before wiring

All complete playbooks will state that the plan-utilities skip can only be returned by `zpps-planning-ponytail`. The kernel's pre-action contract for `wire` will require the same-revision Ponytail result whenever the accepted change has executable responsibilities. `zpp-auto` will make same-invocation transfer explicit so handoff acknowledgement cannot terminate triage successfully.

This retains caller-owned sequence selection: the kernel validates predecessor evidence but never chooses or invokes Ponytail. Reintroducing the superseded kernel dispatcher was rejected because it would conflict with the current complete-playbook architecture.

### Validate structural component order, not arbitrary prose

The packaged workflow loader will derive normalized explicit component uses from playbook Markdown and validate that every complete playbook places `zpps-planning-ponytail` before `zpps-wire`; `zpp-auto` remains a triage-only exception but must name its complete handoff targets. Focused pure-function tests will cover missing, reversed, and valid component sequences. This checks a product-bearing structural contract without pinning descriptive wording.

## Risks / Trade-offs

- [Registered roots may be nested] → Resolve the most-specific root before classifying the OpenSpec boundary, matching Bundler ownership semantics.
- [An ignored path could conceal an unauthorized repository] → Ignore only paths beneath a known registered root; unknown roots remain violations.
- [Prompt execution can still fail outside ZPP's runtime] → Make the handoff and Ponytail receipt explicit in every relevant skill and enforce structural presence during packaging plus predecessor evidence at the kernel boundary.
- [Markdown parsing can become brittle] → Parse only normalized backtick component-use tokens in numbered playbook sections and test invalid order independently of narrative text.

## Migration Plan

1. Shape a public audit regression in `features/openspec_bundler_integration/` and focused structural utility failures in unit tests.
2. Implement ZPP path classification and expose ignored-path evidence through the CLI.
3. Implement and validate structural playbook component extraction and ordering.
4. Update `zpp-auto`, complete playbooks, and the kernel to require same-invocation handoff and actual Ponytail outcomes.
5. Run focused BDD/unit targets, the complete repository gates, synchronize canonical specs, and archive only with explicit authority.

