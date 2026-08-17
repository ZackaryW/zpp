from __future__ import annotations

import support
from agent_router import Agent
from behave import given, then, when


@given("the packaged workflow assets are loaded")
def load_packaged_assets(context) -> None:
    context.skill = support.load_skill()
    context.documents = support.load_trait_documents()


@then("the packaged skill is named zpp-workflow")
def skill_is_named(context) -> None:
    assert context.skill.name == "zpp-workflow", context.skill.name


@then("the packaged skill is compatible with every supported agent")
def skill_is_compatible(context) -> None:
    assert context.skill.compatible_agents == frozenset(Agent)


@then("the packaged skill carries a SKILL.md document")
def skill_carries_document(context) -> None:
    assert any(item.relative_path == "SKILL.md" for item in context.skill.files)


@then("no workflow authority family is packaged")
def no_workflow_family(context) -> None:
    packaged = set(context.documents) & support.WORKFLOW_AUTHORITY_FAMILIES
    assert not packaged, packaged


@then("the packaged trait families are exactly the standard collection")
def standard_collection(context) -> None:
    assert set(context.documents) == support.STANDARD_COLLECTION


@when("the bdd-execution family is decoded")
def decode_execution(context) -> None:
    context.execution = context.documents["bdd-execution"]["trait"]


@then(
    "its flavors declare the manual disabled complete and targeted modes "
    "with a trailing default"
)
def execution_modes(context) -> None:
    modes = [flavor.get("facet", {}).get("bdd_mode") for flavor in context.execution]
    assert modes == ["manual", "disabled", "complete", "targeted", None], modes


@then("every bdd-execution flavor carries a non-empty body")
def execution_bodies(context) -> None:
    assert all(flavor["content"]["body"].strip() for flavor in context.execution)


@when("the zero-assumptions and tooling families are decoded")
def decode_universal(context) -> None:
    context.zero_assumptions = context.documents["zero-assumptions"]
    context.tooling = context.documents["tooling"]["trait"]


@then("zero-assumptions declares always-run activation")
def zero_assumptions_activation(context) -> None:
    assert context.zero_assumptions["meta"]["activation"] == "always-run"


@then("tooling declares exactly the rg and jq facets")
def tooling_facets(context) -> None:
    tools = [flavor["facet"]["tool"] for flavor in context.tooling]
    assert tools == ["rg", "jq"], tools
