---
name: learn-zpp
description: Ground explanations, diagnosis, configuration guidance, integrations, and proposed changes involving zpp in target-specific resolver evidence. Use whenever a zpp decision depends on governance mode, effective configuration, source precedence, isolation, supporting-tool behavior, or an uncertain Git or CLI assumption. This skill is read-only and routes mutations to the appropriate existing workflow.
---

# Learn zpp

Establish what zpp does for the concrete target before explaining or changing it. Treat memory, nearby repositories, and plausible examples as leads only.

## Ground the target

1. Name the exact directory or file whose behavior matters. Do not substitute the repository root.
2. Run both commands against that same target:

   ```text
   zpp resolve <target> --json
   zpp config resolve <target> --sources --json
   ```

3. Read `zpp <command> --help` before asserting command shape or available flags.
4. Separate the evidence:
   - Use `resolve` for governance mode, matched rule, governing root or store, and isolation context.
   - Use `config resolve` for effective values, winning origins, and ordered source layers.
5. If a result is degraded or the toolchain is suspect, run `zpp doctor <target> --json`. Diagnosis stays read-only.

Read [resolver evidence](references/resolver-evidence.md) when interpreting modes, config layers, nested targets, or common resolver traps.

## Check the contract

For a behavior question, compare the live result with the governing capability under `openspec/specs/` and the current implementation or tests. For a proposed behavior change, also inspect the active OpenSpec change. Do not treat one of these as a substitute for the others:

- Resolver output says what this target receives now.
- OpenSpec says what the product promises.
- Code and tests show how the promise is implemented and guarded.

When external-tool semantics affect the conclusion, use that tool's live help and current authoritative upstream documentation. Never accept or reject a Git submodule, subtree, package-manager, or plugin-discovery claim without that evidence. For submodules, distinguish the cloneable repository URL, the downstream mount path, the pinned gitlink commit, and optional branch-following configuration; none of those terms is evidence for an upstream subdirectory selector.

## Report one evidence note

Use this format for every conclusion:

```text
Target: <canonical target>
Observed: <commands and decisive fields>
Contract: <spec/code/upstream sources checked>
Conclusion: <what the evidence supports>
Uncertainty: <none, or the bounded gap>
Handoff: <none, or the workflow that owns the mutation>
```

Keep facts and inference distinct. If evidence conflicts, state the conflict and stop short of inventing behavior.

## Route mutations

Do not install tools, write config, provision isolation, edit resolver code, or create OpenSpec artifacts from this skill. Preserve the evidence note and hand the work to its owner.

Read [mutation routing](references/mutation-routing.md) when the next step would change tools, configuration, governance state, specs, or production code.
