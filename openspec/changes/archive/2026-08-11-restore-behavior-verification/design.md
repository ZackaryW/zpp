## Context

ZPP 2.0 retained `bdd-execution` policy but removed the executable behavior-verification surface. The adopted ZPP 1.x contract already established a repository-owned `zpp.behave.yaml`, deterministic affected selection, three explicit provider adapters, and optional OpenLease reconciliation cross-checks. The port must preserve that public behavior while fitting ZPP 2.0's established module boundaries and current OpenLease direct-document API.

OpenLease now supports invocation-scoped direct document bindings for an unregistered repository. That removes the former need to create or select a space for repository trait resolution and ordinary `zpp behave` CLI use. A native agent hook may call ZPP from the current worktree, while ZPP discovers the Git root and performs the direct bindings internally; the agent receives resolved policy without knowing OpenLease topology or space concepts.

## Goals / Non-Goals

**Goals:**

- Restore the complete version-1 `zpp behave` command and configuration contract.
- Preserve deterministic, declaration-bounded selection and shell-free provider execution.
- Register `zpp.behave` independently from `zpp.traits` while constructing both through the same ZPP OpenLease adapter.
- Keep repository hook resolution and direct behavior execution independent of OpenLease spaces while preserving explicitly selected reconciliation cross-checks in real OpenLease repository or cohort context.
- Integrate behavior verification with the single `zpp-workflow` skill and its resolved `bdd-execution` policy.
- Keep implementation under the existing `core`, `cli`, `artifacts`, and `utils` package shape.

**Non-Goals:**

- Migrating or translating obsolete OpenLease state, legacy gate names, or other ZPP 1.x runtime state.
- Recreating the old top-level `zpp.behavior` package or importing the old engine as a fallback.
- Inferring commands, providers, gates, or executable arguments from agent text or installed tools.
- Creating an OpenLease space for direct CLI execution or simulating repository/cohort callbacks without reconciliation context.
- Adding a public trait authoring command beyond the existing exact trait initialization surface.

## Decisions

### Reimplement the adopted contract in the current package shape

Behavior schema, target selection, and operation input/output models belong in `zpp.core`. The public Typer command belongs in `zpp.cli`. Git/path/glob inspection, process adapters, and OpenLease binding belong in `zpp.utils`. Packaged workflow and trait wording remain in `zpp.artifacts`.

This keeps the architecture the owner already established for ZPP 2.0. Copying the old top-level package would be mechanically easy but would restore a discarded shape and split domain ownership again.

### Keep `zpp.behave.yaml` as a dedicated independent extension document

ZPP registers `zpp.behave` independently of `zpp.traits`. The root YAML mapping is owned wholly by that extension, so OpenLease receives an `ExtensionDocumentBinding` with YAML codec, dedicated layout, repository-path provenance, and exact write authority for initialization.

For `zpp behave init` or execution, ZPP discovers the containing Git worktree root and binds `<root>/zpp.behave.yaml` directly. Initialization uses OpenLease's bounded initialization with `{"version": 1, "commands": {}}`; execution is read-only. Neither path registers repository topology or creates a space.

Embedding behavior configuration into trait TOML was rejected because traits specialize agent policy while behavior declarations authorize a bounded public process surface. Combining them would blur configuration ownership and make selection side effects easier to misread.

### Preserve one strict mapping and deterministic selection pipeline

The version-1 schema remains closed and repository-owned. Each command declares exactly one provider, a closed ordered target map, and optional command-local gates. Each target has a unique provider value and one or more validated repository-relative path patterns.

Selection happens only after the entire mapping and invocation are validated. Explicit target, gate, complete, and revision-range modes are mutually exclusive. With no override, working-tree evidence includes `HEAD`, staged, unstaged, and untracked non-ignored paths. Any invalid, unmapped, or uncertain changed path broadens selection to every declared target; it never narrows execution speculatively.

### Use an explicit shell-free provider registry

The default registry contains `argv`, `nx`, and `go-task`. Adapters validate closed settings and return one argv tuple; the process runner executes it without a shell. A host may inject another conforming adapter when constructing the extension, but runtime discovery from packages, entry points, PATH tools, or agent output is prohibited.

Nx discovery retains the adopted repository-first order: package-local wrapper, repository-root wrapper backed by `.nx/installation`, then PATH. Go Task may use a configured executable or safe repository/PATH discovery. Availability diagnostics are informational during initialization and never choose a provider.

### Keep direct binding behind ZPP's public surfaces

The native SessionStart hook invokes trait resolution from the current directory. ZPP discovers the worktree and directly binds the repository trait documents; it does not create a temporary space or require the agent to understand OpenLease. The hook does not initialize or execute `zpp.behave.yaml`.

The explicit `zpp behave` command discovers the same worktree and directly binds its dedicated YAML before invoking `initialize` or `run`. Behavior execution remains explicit because it can start repository processes; merely installing a hook or authoring the file starts no verification.

### Preserve opt-in OpenLease reconciliation cross-checks

`zpp.behave` also exposes `run` for repository and cohort callback targets and declares the adopted pre-repository gate/observe and post-repository/post-cohort observe callbacks. Registration is inert. A reconciliation plan must explicitly select the extension, operation, event, mode, command, selection mode, and real target context.

The callback handler obtains the exact target worktree from OpenLease's repository or cohort context, then opens that repository's root `zpp.behave.yaml` through the same direct document binding used by the CLI. It must not read or require an extension-managed callback configuration source, create a temporary repository or space, or expose coordination details to the agent.

### Let `bdd-execution` advise the consolidated workflow's explicit command

The resolved trait remains advisory and cannot establish completion or skip a workflow stage. The workflow invokes a repository-declared behavior command only when the accepted BDD obligation and resolved mode require it:

- `manual`: pause for an explicit verification choice.
- `disabled`: omit behavior execution only with independently observed alternate evidence and no remaining shaped BDD obligation.
- `complete`: invoke the selected command with `--all`.
- `targeted` or default: use `--gate zpp-workflow` when that command declares the gate; otherwise use default deterministic affected selection.

The gate identity follows the installed skill identity, `zpp-workflow`. Old `zpp-flow-*` gate identities receive no alias or migration path.

## Risks / Trade-offs

- **Port drift from the adopted implementation** → Reuse the existing canonical behavior specification as the baseline, add fail-first contract tests, and compare public CLI/YAML/provider cases rather than copying files blindly.
- **A hook could be mistaken for automatic verification** → Keep the hook limited to trait resolution and test that it neither initializes nor executes repository behavior.
- **Callback registration could be mistaken for activation** → Require explicit callback selection and test that an unselected callback starts no process.
- **Direct binding could be confused with a temporary space** → Assert that hook resolution, direct behavior commands, and callback-time document reopening create no additional topology, temporary space, or persistent binding.
- **Provider validation can execute inspection subprocesses** → Complete mapping validation precedes configured verification, adapters use shell-free argv, and any unavailable surface fails closed without provider fallback.
- **Unknown changed paths make targeted verification broader** → Preserve the conservative all-target fallback; this costs time but avoids false claims that affected verification is complete.
- **A generic `behave` name can be confused with Python Behave** → Documentation and help consistently describe the command as repository-owned behavior verification; provider choice remains repository-defined.

## Migration Plan

1. Add fail-first tests for the adopted mapping, selection, provider, CLI, direct binding, hook-isolation, opt-in callback, and workflow contracts.
2. Implement the engine within current package boundaries and register `zpp.behave` beside `zpp.traits`.
3. Reconcile packaged `bdd-execution` wording and the consolidated skill around `zpp-workflow`.
4. Validate existing version-1 `zpp.behave.yaml` fixtures without rewriting them and build the ZPP 2.0 artifact.
5. Treat any obsolete extension state or legacy gate identity as unsupported; rollback is removal of the new behavior surface, with repository-authored YAML left untouched.

## Open Questions

None.
