from __future__ import annotations

import support
from agent_router import Agent
from behave import given, then, when

from zpp.artifacts import (
    OPENSPEC_ADAPTER_SKILL_NAMES,
    REPOSITORY_EVIDENCE_SKILL_NAME,
    WORKFLOW_ENTRY_SKILL_NAMES,
    WORKFLOW_KERNEL_SKILL_NAME,
    WORKFLOW_SKILL_NAMES,
    WORKFLOW_STAGE_SKILL_NAMES,
)


@given("the packaged workflow family is available")
def workflow_family_available(context) -> None:
    context.family = support.load_workflow_family()


@when("the current workflow family is loaded")
def load_current_family(context) -> None:
    context.names = tuple(skill.name for skill in context.family)


@then("the five entries precede the kernel and seven stages")
def entries_kernel_and_stages_are_ordered(context) -> None:
    expected = (
        *WORKFLOW_ENTRY_SKILL_NAMES,
        WORKFLOW_KERNEL_SKILL_NAME,
        *WORKFLOW_STAGE_SKILL_NAMES,
    )
    assert context.names[: len(expected)] == expected, context.names


@then("every packaged workflow member is valid for every supported agent")
def every_member_is_cross_agent(context) -> None:
    assert all(skill.compatible_agents == frozenset(Agent) for skill in context.family)
    assert all(
        any(item.relative_path == "SKILL.md" for item in skill.files)
        for skill in context.family
    )


@when("the OpenSpec operation coverage is inspected")
def inspect_adapter_coverage(context) -> None:
    context.names = tuple(skill.name for skill in context.family)


@then("the eleven exact adapters are packaged in deterministic order")
def exact_adapter_coverage(context) -> None:
    start = len(WORKFLOW_ENTRY_SKILL_NAMES) + 1 + len(WORKFLOW_STAGE_SKILL_NAMES)
    actual = context.names[start : start + len(OPENSPEC_ADAPTER_SKILL_NAMES)]
    assert actual == OPENSPEC_ADAPTER_SKILL_NAMES, actual


@then("onboarding and broad operation aliases are absent")
def excluded_operation_identities_are_absent(context) -> None:
    excluded = {
        "zpps-onboard",
        "zpps-plan-change",
        "zpps-verify",
        "zpps-archive",
    }
    assert not excluded & set(context.names), context.names


@then("repository verification is one separate final family member")
def repository_verifier_is_separate(context) -> None:
    assert context.names[-1] == REPOSITORY_EVIDENCE_SKILL_NAME, context.names
    assert REPOSITORY_EVIDENCE_SKILL_NAME not in OPENSPEC_ADAPTER_SKILL_NAMES


@when("the packaged trait collection is decoded")
def decode_traits(context) -> None:
    context.documents = support.load_trait_documents()


@then("only the five contextual trait families remain")
def contextual_traits_remain(context) -> None:
    assert set(context.documents) == {
        "bdd",
        "bdd-execution",
        "bdd-structure",
        "tdd",
        "tooling",
    }


@then("BDD execution retains its five repository-selected modes")
def execution_modes_remain(context) -> None:
    flavors = context.documents["bdd-execution"]["trait"]
    actual = [flavor.get("facet", {}).get("bdd_mode") for flavor in flavors]
    assert actual == ["manual", "disabled", "complete", "targeted", None], actual


@then("the workflow family has the exact canonical identity sequence")
def canonical_identity_sequence(context) -> None:
    assert context.names == WORKFLOW_SKILL_NAMES, context.names
