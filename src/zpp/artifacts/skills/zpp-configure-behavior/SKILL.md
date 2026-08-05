---
name: zpp-configure-behavior
description: Create or revise a repository's committed zpp.behave.yaml affected-verification mapping through ZPP's validated public surface. Use when onboarding mapped verification, reorganizing BDD targets, changing impact relationships, or reconciling established Nx or provider-neutral runner targets.
---

# Configure repository behavior

Keep executable discovery, selection, and execution in ZPP core. This skill owns
only explicit agent-assisted authoring of the committed declarative mapping.

1. Resolve the Git worktree root and inspect its established test runners,
   capability boundaries, build configuration, and existing `zpp.behave.yaml`.
2. Run `zpp behave init`. Preserve a valid existing mapping. Use its report to
   inspect the existing Nx project/target surface when Nx is available; never
   install, migrate, download, connect, or configure Nx or its plugins.
3. Propose named commands, closed target sets, and repository-relative impact
   globs from evidence in the repository. Preserve the established runner.
   Prefer capability-cohesive targets and map shared inputs to every affected
   target. Leave uncertainty conservative: an unmapped path selects all.
4. Write only `zpp.behave.yaml`. Use a provider-neutral typed argv declaration
   when Nx is absent or unsuitable. Use an Nx declaration only for projects and
   targets already exposed by the repository. Never obtain runtime executable
   text or undeclared target names from agent output.
5. Run `zpp behave init` again to validate the complete mapping. Correct every
   schema, duplicate-key, provider, path, or target error before continuing.
6. Run the separately configured audit command with `--all`. Completion requires
   a valid committed mapping and a green complete audit through ZPP.

Pause only when the repository does not establish its runner/provider boundary
or the owner must choose a new verification boundary. A missing executable for
an explicitly configured provider is a repository prerequisite, not permission
to switch providers or install tooling. On success, hand the validated mapping
and audit evidence back to the invoking workflow or user.

The skill may mutate the mapping only with the current session's authority. It
does not grant install, commit, provider, plugin, or failed-gate bypass authority.
