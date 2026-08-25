from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from zpp.artifacts import (
    COMPLETE_WORKFLOW_SKILL_NAMES,
    WORKFLOW_SKILL_NAMES,
    WORKFLOW_STAGE_SKILL_NAMES,
    packaged_component_contracts,
    packaged_workflow_contract_schemas,
    packaged_workflow_contracts,
)
from zpp.core.workflows import (
    WorkflowContractError,
    decode_component_contract,
    decode_workflow_contract,
    validate_contract_inventory,
)


def _workflow_payload() -> dict[str, object]:
    return {
        "version": 1,
        "name": "zpp-new-feature",
        "mode": "reminder",
        "stages": [
            {"id": "clarify", "component": "zpps-clarify"},
            {"id": "shape-bdd", "component": "zpps-shape-bdd"},
        ],
    }


def _component_payload() -> dict[str, object]:
    return {
        "version": 1,
        "name": "zpps-clarify",
        "kind": "stage",
        "effect": "read-only",
        "standalone": True,
        "results": ["completed", "blocked", "exploration-required"],
    }


def test_strict_contract_decoders_return_frozen_typed_models() -> None:
    workflow = decode_workflow_contract(
        _workflow_payload(), source="workflow.json"
    )
    component = decode_component_contract(
        _component_payload(), source="component.json"
    )

    assert workflow.stages[0].component == "zpps-clarify"
    assert component.effect == "read-only"
    with pytest.raises(FrozenInstanceError):
        workflow.name = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "diagnostic"),
    [
        ("unknown", True, "unknown"),
        ("version", True, "version"),
        ("mode", "enforcing", "mode"),
    ],
)
def test_workflow_decoder_rejects_unknown_or_invalid_typed_fields(
    field: str,
    value: object,
    diagnostic: str,
) -> None:
    payload = _workflow_payload()
    payload[field] = value

    with pytest.raises(WorkflowContractError, match=diagnostic) as observed:
        decode_workflow_contract(payload, source="bad-workflow.json")

    assert "bad-workflow.json" in str(observed.value)


def test_workflow_decoder_rejects_duplicate_stage_identifiers() -> None:
    payload = _workflow_payload()
    stages = payload["stages"]
    assert isinstance(stages, list)
    stages.append({"id": "clarify", "component": "zpps-wire"})

    with pytest.raises(WorkflowContractError, match="duplicate stage id"):
        decode_workflow_contract(payload, source="duplicate.json")


def test_component_decoder_rejects_unknown_fields_and_duplicate_results() -> None:
    unknown = _component_payload()
    unknown["extra"] = "invalid"
    with pytest.raises(WorkflowContractError, match="extra"):
        decode_component_contract(unknown, source="bad-component.json")

    duplicate = _component_payload()
    duplicate["results"] = ["completed", "completed"]
    with pytest.raises(WorkflowContractError, match="duplicate result"):
        decode_component_contract(duplicate, source="duplicate-component.json")


def test_inventory_validation_rejects_missing_and_unknown_references() -> None:
    workflow = decode_workflow_contract(_workflow_payload(), source="workflow.json")
    component = decode_component_contract(
        _component_payload(), source="component.json"
    )

    with pytest.raises(WorkflowContractError, match="missing workflow contract"):
        validate_contract_inventory(
            (workflow,),
            (component,),
            workflow_names=("zpp-new-feature", "zpp-fix-bug"),
            component_names=("zpps-clarify",),
        )

    with pytest.raises(WorkflowContractError, match="unknown component"):
        validate_contract_inventory(
            (workflow,),
            (component,),
            workflow_names=("zpp-new-feature",),
            component_names=("zpps-clarify",),
        )


def test_packaged_contract_inventory_is_complete_and_cross_referenced() -> None:
    workflows = packaged_workflow_contracts()
    components = packaged_component_contracts()

    assert tuple(item.name for item in workflows) == COMPLETE_WORKFLOW_SKILL_NAMES
    expected_components = tuple(
        name for name in WORKFLOW_SKILL_NAMES if name.startswith("zpps-")
    )
    assert tuple(item.name for item in components) == expected_components
    assert all(
        tuple(stage.component for stage in workflow.stages)
        == WORKFLOW_STAGE_SKILL_NAMES
        for workflow in workflows
    )
    assert "zpp-workflow" not in {item.name for item in workflows}


def test_packaged_contract_schemas_are_typed_json_resources() -> None:
    schemas = packaged_workflow_contract_schemas()

    assert tuple(item.name for item in schemas) == (
        "component-contract.schema.json",
        "workflow-contract.schema.json",
    )
    assert all(item.document["type"] == "object" for item in schemas)
    assert all(item.document["additionalProperties"] is False for item in schemas)
