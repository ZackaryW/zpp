# Reference behavior inventory

The ZPP 1.x standard-workflow collection is design evidence, not a runtime
migration source. ZPP 2.0 reauthors each applicable behavior as follows:

| Reference document | ZPP 2.0 owner |
| --- | --- |
| `automatic-workflow.md` | `skills/zpp-workflow/SKILL.md` |
| `workflow-authority.md` | `skills/zpp-workflow/SKILL.md` |
| `bdd-structure-python.md` | `traits/bdd-structure.toml` Python flavor |
| `bdd-structure-flutter.md` | `traits/bdd-structure.toml` Flutter flavor |
| `bdd-structure-ts.md` | `traits/bdd-structure.toml` TypeScript flavor |
| `python-bdd.md` | `traits/bdd.toml` Python flavor |
| `flutter-bdd.md` | `traits/bdd.toml` Flutter flavor |
| `typescript-bdd.md` | `traits/bdd.toml` TypeScript flavor |
| `python-tdd.md` | `traits/tdd.toml` Python flavor |
| `python-django-tdd.md` | `traits/tdd.toml` Django flavor |
| `flutter-tdd.md` | `traits/tdd.toml` Flutter flavor |
| `typescript-tdd.md` | `traits/tdd.toml` TypeScript flavor |
| `bdd-workflow.md` | `traits/bdd-workflow.toml` mode flavors and targeted default |
| `python-build.md` | `traits/build.toml` Python flavor |
| `proportionate-dependencies.md` | `traits/dependencies.toml` |
| `use-rg.md` | `traits/tooling.toml` rg flavor |
| `use-jq.md` | `traits/tooling.toml` jq flavor |
| `use-zmem.md` | `traits/tooling.toml` zmem flavor |
| `lease-complete-affected-set.md` | `traits/lease-complete-affected-set.toml` |
| `lease-conflict-policy.md` | `traits/lease-conflict-policy.toml` |
| `reconciliation-gate.md` | `traits/reconciliation-gate.toml` |
| `zero-assumptions.md` | `traits/zero-assumptions.toml` |

No reference document is loaded at runtime, and no `workflow.toml` is packaged.
