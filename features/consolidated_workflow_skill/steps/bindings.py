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


@then("the six entries precede the kernel and seven stages")
def entries_kernel_and_stages_are_ordered(context) -> None:
    expected = (
        *WORKFLOW_ENTRY_SKILL_NAMES,
        WORKFLOW_KERNEL_SKILL_NAME,
        *WORKFLOW_STAGE_SKILL_NAMES,
    )
    assert context.names[: len(expected)] == expected, context.names


@then("the six workflow entries have the canonical entry order")
def workflow_entries_have_canonical_order(context) -> None:
    assert WORKFLOW_ENTRY_SKILL_NAMES == support.EXPECTED_WORKFLOW_ENTRY_NAMES


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


@when("the registered playbook guidance is inspected")
def inspect_registered_playbooks(context) -> None:
    context.documents = support.skill_documents(context.family)
    context.contracts = support.load_workflow_contracts()


@then("clear defect triage enters the registered fix-bug playbook")
def clear_defect_enters_fix_bug(context) -> None:
    document = context.documents["zpp-auto"]
    assert "zpp-fix-bug" in document
    assert any(item.name == "zpp-fix-bug" for item in context.contracts)


@then("mixed product triage enters the registered generic playbook")
def mixed_triage_enters_generic(context) -> None:
    document = context.documents["zpp-auto"]
    assert "zpp-generic-workflow" in document
    assert any(item.name == "zpp-generic-workflow" for item in context.contracts)


@then("a genuine non-match declares no reminder start")
def genuine_non_match_is_unregistered(context) -> None:
    document = context.documents["zpp-auto"]
    assert "no-handoff" in document
    assert all(item.name != "zpp-auto" for item in context.contracts)


@then("handoff alone is not accepted as selected-playbook completion")
def handoff_is_not_completion(context) -> None:
    document = context.documents["zpp-auto"]
    assert "selected playbook" in document
    assert "start" in document


@then("the obsolete generic workflow identity has no contract")
def obsolete_identity_has_no_contract(context) -> None:
    assert all(item.name != "zpp-workflow" for item in context.contracts)


@then("each complete entry contract begins with clarify")
def complete_entries_begin_with_clarify(context) -> None:
    assert all(item.stages[0].component == "zpps-clarify" for item in context.contracts)


@then("each declared stage remains a distinct registered component action")
def stages_are_distinct_actions(context) -> None:
    for contract in context.contracts:
        components = [stage.component for stage in contract.stages]
        assert len(components) == len(set(components)), contract
