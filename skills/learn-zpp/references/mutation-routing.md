# Mutation routing

Preserve the evidence note and route the smallest required change.

| Evidence shows | Hand off to | Do not do here |
|---|---|---|
| zpp or a governed dependency is missing or stale | the zpp bootstrap workflow | install or upgrade tools |
| existing target config is wrong but the contract already supports the desired result | the repository's governed configuration/implementation workflow | write `zpp.toml` |
| isolation reports provisioning required | the explicit workset provisioning workflow named by zpp | create branches or worktrees during diagnosis |
| the promised resolver/config behavior must change | OpenSpec clarification/proposal, then the implementation workflow after acceptance | edit production code or specs |
| an accepted OpenSpec change is ready | the OpenSpec apply workflow with its resolved BDD/TDD policy | bypass fail-first governance |
| external-tool behavior is uncertain | live help plus authoritative upstream documentation | turn a remembered constraint into architecture |

Bootstrap, provisioning, proposal, and apply are separate permissions. Diagnosis does not imply authorization for any of them.

