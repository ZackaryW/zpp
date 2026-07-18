# trait-system

## MODIFIED Requirements

### Requirement: Trait application tiers with session env override
The active trait set SHALL be computed from the existing config layering — store defaults, then the member's resolved workset profile, then repo `zpp.toml` — as a `[traits] apply` list per tier, unioned in tier order. When the `ZPP_TRAITS` environment variable is set (comma-separated names), it SHALL replace the workset-profile tier only, for that invocation; store and repo tiers SHALL always survive an env override.

#### Scenario: Env replaces only the personal tier
- **WHEN** the member's profile applies `["coverage"]`, the repo applies `["structure"]`, and `ZPP_TRAITS=ponytail` is set
- **THEN** the effective set is the store tier plus `ponytail` plus `structure` — `coverage` is absent and `structure` cannot be removed by the env

#### Scenario: Profile-applied traits reach every member
- **WHEN** a workset's `default` profile applies `["ponytail"]` and a member repo applies nothing itself
- **THEN** that member's `zpp trait effective` includes ponytail attributed to the workset tier

#### Scenario: Provenance names the env tier
- **WHEN** `ZPP_TRAITS` is active
- **THEN** `zpp trait effective --json` attributes env-applied traits to `env`, not `workset`
