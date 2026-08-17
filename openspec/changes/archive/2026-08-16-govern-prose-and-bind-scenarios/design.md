## Context

Three governance layers can describe the packaged workflow skill independently: the canonical specification, the shipped `SKILL.md` wording, and the literal phrase assertions in `verify_workflow_contract`. Nothing forces them to move together.

Two accepted changes removed two of those layers for skill prose within twenty-two minutes. `enforce-feature-traceability` established that tests SHALL NOT pin arbitrary artifact wording, which withdraws the assertion layer as legitimate governance. The artifact-only maintenance route then withdrew canonical specification reconciliation by naming packaged skill and trait prose as bypass-eligible. The combination leaves the shipped wording governed by nothing, and the route was itself introduced through the route it created.

The canonical specification already treats this wording as observable behavior. Several accepted scenarios read `WHEN a user inspects the consolidated workflow skill THEN it contains ...`. The route's premise, that packaged skill prose is non-runtime artifact text, contradicts that accepted framing.

## Goals / Non-Goals

**Goals:**

- Keep artifact-only maintenance for artifacts no canonical requirement describes.
- Restore canonical specification reconciliation as the governing layer for the packaged workflow skill and packaged trait documents.
- Give the shipped monorepo behavior-ownership paragraph a canonical requirement.

- Make the scenario binding obligation a shipped rule rather than a local convention.
- Bring this repository into compliance with its own shipped guidance.

**Non-Goals:**

- Adding runtime, CLI, trait, or hook behavior.
- Revisiting whether `enforce-feature-traceability` should have withdrawn the assertion layer.
- Replacing Behave, restructuring capability roots, or changing verification providers.

## Decisions

**Spec-governed status is determined by whether a canonical requirement describes the artifact's content, not by file location or extension.** A path allowlist would drift as artifacts move, and the role-directory restructure already relocated every packaged skill once. Naming the property keeps classification correct across future moves. The requirement names the three current members concretely so the rule is usable without re-deriving it.

**A spec-governed artifact change reconciles canonical specifications even when it changes no executable behavior.** This is the operative clause. Without it, a skill-prose change could still enter the workflow, declare every conditional stage not applicable including `form-specs`, and reproduce the drift through a longer path.

**Artifact-only maintenance stays rather than being reverted.** README and reference documentation genuinely have no canonical requirement behind them, and forcing them through seven stages recreates the pressure that produced the route. The defect is its scope, not its existence.

**Monorepo ownership becomes its own requirement rather than scenarios under behavior-only feature shaping.** It constrains where behavior is shaped rather than what may be shaped, it carries its own inspection and escalation obligations, and `Behavior-only feature shaping` is already a two-paragraph requirement with three scenarios.

**The binding obligation ships in the packaged `bdd` guidance rather than only in the workflow skill.** The skill governs one workflow run; the trait is what a consuming repository resolves as standing policy. `bdd.toml` already directs Behave at "integration behavior exercised through the public system," so the rule is a sharpening of existing guidance rather than a new concern. Stating it in the trait is what makes this repository's recorder bindings a violation rather than a local style choice.

**Scenario-selected verification replaces the capability-wide block.** Today `verify_capability(name)` dispatches to one function per capability, executed after every scenario in that root, so twenty-six scenarios run one identical assertion set. The `lru_cache` on `verify_openspec_skill_provisioning_contract` exists only to suppress that repetition and is removed with the design that required it.

**Withdrawn scenarios must already exist as canonical requirements.** Most of `consolidated_workflow_skill`'s scenarios describe agent conduct during a workflow run, which nothing executes. Each withdrawal is checked against the canonical specification first, and a missing requirement is added before the scenario is removed, so the obligation moves rather than disappears.

## Risks / Trade-offs

Editing packaged skill wording now costs a full OpenSpec change. That is the intended cost, and the archived `enforce-feature-traceability` change shows the shape is manageable at seven files, but it will make small wording corrections feel disproportionate. The mitigation is that the route remains available for every artifact no requirement describes.

Withdrawing scenarios reduces the visible scenario count sharply, most of all in `consolidated_workflow_skill`. A smaller suite that actually exercises the system is the intent, but the count drop will look like lost coverage and should be read against the canonical specification that absorbs each withdrawn obligation.

The requirements governing agent conduct remain unenforced by any test, and deliberately so. Once wording assertions are withdrawn, conduct requirements are enforced by the acting agent reading the specification, which is the same mechanism every other requirement in this capability already relies on. This change makes that honest rather than simulating enforcement through phrase matching.

Steps 4 and 5 are sequenced so verification never passes on a false basis: wording assertions are withdrawn only after their obligations are confirmed present in the canonical specification, and recorder bindings are replaced before the scenarios depending on them are judged.
