"""Strict workflow contracts and immutable reminder transitions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError

NonEmptyString = Annotated[str, Field(min_length=1)]
WorkflowMode = Literal["reminder"]
ComponentKind = Literal["kernel", "stage", "operation", "evidence"]
EffectClass = Literal["read-only", "planning", "product", "coordination", "lifecycle"]
StageStatus = Literal["pending", "completed", "skipped"]


class WorkflowContractError(ValueError):
    """A workflow contract or reminder transition is invalid."""


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class _RawStage(_ClosedModel):
    id: NonEmptyString
    component: NonEmptyString


class _RawWorkflow(_ClosedModel):
    version: int
    name: NonEmptyString
    mode: WorkflowMode
    stages: list[_RawStage] = Field(min_length=1)


class _RawComponent(_ClosedModel):
    version: int
    name: NonEmptyString
    kind: ComponentKind
    effect: EffectClass
    standalone: bool
    results: list[NonEmptyString] = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class WorkflowStageContract:
    id: str
    component: str


@dataclass(frozen=True, slots=True)
class WorkflowContract:
    version: int
    name: str
    mode: WorkflowMode
    stages: tuple[WorkflowStageContract, ...]


@dataclass(frozen=True, slots=True)
class ComponentContract:
    version: int
    name: str
    kind: ComponentKind
    effect: EffectClass
    standalone: bool
    results: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkflowStageState:
    id: str
    component: str
    status: StageStatus = "pending"
    result: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowRun:
    run_id: UUID
    workflow: str
    root: Path
    change: str
    stages: tuple[WorkflowStageState, ...]
    observed_bundle: UUID | None = None


@dataclass(frozen=True, slots=True)
class WorkflowCheck:
    status: str
    allowed: bool
    sequence_match: bool | None
    workflow: str | None
    expected_stage: WorkflowStageState | None
    unfinished_stages: tuple[WorkflowStageState, ...]
    warning: str | None = None


def _source_error(source: str, error: object) -> WorkflowContractError:
    return WorkflowContractError(f"{source}: {error}")


def decode_workflow_contract(
    configuration: Mapping[str, object], *, source: str
) -> WorkflowContract:
    try:
        raw = _RawWorkflow.model_validate(dict(configuration), strict=True)
        if raw.version != 1:
            raise ValueError("version must be integer 1")
        stage_ids = [stage.id for stage in raw.stages]
        duplicate_ids = sorted(
            {stage_id for stage_id in stage_ids if stage_ids.count(stage_id) > 1}
        )
        if duplicate_ids:
            raise ValueError(f"duplicate stage id: {duplicate_ids[0]}")
        return WorkflowContract(
            raw.version,
            raw.name,
            raw.mode,
            tuple(
                WorkflowStageContract(stage.id, stage.component) for stage in raw.stages
            ),
        )
    except (ValidationError, TypeError, ValueError) as error:
        if isinstance(error, WorkflowContractError):
            raise
        raise _source_error(source, error) from error


def decode_component_contract(
    configuration: Mapping[str, object], *, source: str
) -> ComponentContract:
    try:
        raw = _RawComponent.model_validate(dict(configuration), strict=True)
        if raw.version != 1:
            raise ValueError("version must be integer 1")
        duplicate_results = sorted(
            {result for result in raw.results if raw.results.count(result) > 1}
        )
        if duplicate_results:
            raise ValueError(f"duplicate result: {duplicate_results[0]}")
        return ComponentContract(
            raw.version,
            raw.name,
            raw.kind,
            raw.effect,
            raw.standalone,
            tuple(raw.results),
        )
    except (ValidationError, TypeError, ValueError) as error:
        if isinstance(error, WorkflowContractError):
            raise
        raise _source_error(source, error) from error


def validate_contract_inventory(
    workflows: Sequence[WorkflowContract],
    components: Sequence[ComponentContract],
    *,
    workflow_names: Sequence[str],
    component_names: Sequence[str],
) -> None:
    workflow_map = _unique_contracts(workflows, "workflow")
    component_map = _unique_contracts(components, "component")
    expected_workflows = tuple(workflow_names)
    expected_components = tuple(component_names)
    _require_exact_names(workflow_map, expected_workflows, "workflow")
    _require_exact_names(component_map, expected_components, "component")
    for workflow in workflows:
        for stage in workflow.stages:
            if stage.component not in component_map:
                raise WorkflowContractError(
                    f"workflow {workflow.name!r} references unknown component "
                    f"{stage.component!r}"
                )


def _unique_contracts[T](contracts: Sequence[T], kind: str) -> Mapping[str, T]:
    selected: dict[str, T] = {}
    for contract in contracts:
        name = getattr(contract, "name", None)
        if not isinstance(name, str):
            raise WorkflowContractError(f"{kind} contract has no valid name")
        if name in selected:
            raise WorkflowContractError(f"duplicate {kind} contract: {name}")
        selected[name] = contract
    return MappingProxyType(selected)


def _require_exact_names(
    contracts: Mapping[str, object], expected: Sequence[str], kind: str
) -> None:
    expected_set = set(expected)
    actual_set = set(contracts)
    missing = sorted(expected_set - actual_set)
    unexpected = sorted(actual_set - expected_set)
    if missing:
        raise WorkflowContractError(f"missing {kind} contract: {missing[0]}")
    if unexpected:
        raise WorkflowContractError(f"unexpected {kind} contract: {unexpected[0]}")
    if tuple(contracts) != tuple(expected):
        raise WorkflowContractError(f"{kind} contracts are not in canonical order")


def new_workflow_run(
    contract: WorkflowContract, *, root: Path, change: str
) -> WorkflowRun:
    if not change:
        raise WorkflowContractError("change must be non-empty")
    return WorkflowRun(
        uuid4(),
        contract.name,
        root,
        change,
        tuple(
            WorkflowStageState(stage.id, stage.component) for stage in contract.stages
        ),
    )


def first_pending_stage(run: WorkflowRun) -> WorkflowStageState | None:
    return next((stage for stage in run.stages if stage.status == "pending"), None)


def check_workflow_run(
    run: WorkflowRun | None,
    *,
    component: str,
    workflow: str | None = None,
) -> WorkflowCheck:
    if run is None:
        if workflow is not None:
            return WorkflowCheck(
                "workflow-start-required",
                False,
                None,
                workflow,
                None,
                (),
                f"start the {workflow} reminder before lifecycle work",
            )
        return WorkflowCheck("untracked", True, None, None, None, ())
    expected = first_pending_stage(run)
    unfinished = tuple(stage for stage in run.stages if stage.status == "pending")
    matching = expected is not None and expected.component == component
    warning = None
    if expected is not None and not matching:
        warning = (
            f"out-of-sequence component {component!r}; expected "
            f"{expected.component!r} at stage {expected.id!r}"
        )
    return WorkflowCheck(
        "active",
        True,
        matching,
        run.workflow,
        expected,
        unfinished,
        warning,
    )


def record_workflow_result(
    run: WorkflowRun,
    *,
    component: str,
    result: str,
    accepted_results: frozenset[str],
    observed_bundle: UUID | None = None,
) -> WorkflowRun:
    expected = first_pending_stage(run)
    if (
        expected is None
        or expected.component != component
        or result not in accepted_results
    ):
        return run
    status: StageStatus = (
        "skipped"
        if result in {"skipped", "not-applicable", "accepted-not-applicable"}
        else "completed"
    )
    replacement = replace(expected, status=status, result=result)
    stages = tuple(
        replacement if stage.id == expected.id else stage for stage in run.stages
    )
    return replace(
        run,
        stages=stages,
        observed_bundle=observed_bundle or run.observed_bundle,
    )


def insert_workflow_stage(
    run: WorkflowRun,
    *,
    stage_id: str,
    component: str,
    known_components: frozenset[str],
    before: str | None = None,
    after: str | None = None,
) -> WorkflowRun:
    _validate_new_stage(run, stage_id, component, known_components)
    index = _insertion_index(run, before=before, after=after)
    stages = list(run.stages)
    stages.insert(index, WorkflowStageState(stage_id, component))
    return replace(run, stages=tuple(stages))


def delete_workflow_stage(run: WorkflowRun, *, stage_id: str) -> WorkflowRun:
    index = _stage_index(run, stage_id)
    stages = list(run.stages)
    stages.pop(index)
    if not stages:
        raise WorkflowContractError("workflow must retain at least one stage")
    return replace(run, stages=tuple(stages))


def modify_workflow_stage(
    run: WorkflowRun,
    *,
    stage_id: str,
    component: str,
    known_components: frozenset[str],
) -> WorkflowRun:
    _require_component(component, known_components)
    index = _stage_index(run, stage_id)
    stages = list(run.stages)
    stages[index] = replace(stages[index], component=component)
    return replace(run, stages=tuple(stages))


def upsert_workflow_stage(
    run: WorkflowRun,
    *,
    stage_id: str,
    component: str,
    known_components: frozenset[str],
    before: str | None = None,
    after: str | None = None,
) -> WorkflowRun:
    if any(stage.id == stage_id for stage in run.stages):
        current = next(stage for stage in run.stages if stage.id == stage_id)
        if current.component == component:
            return run
        return modify_workflow_stage(
            run,
            stage_id=stage_id,
            component=component,
            known_components=known_components,
        )
    return insert_workflow_stage(
        run,
        stage_id=stage_id,
        component=component,
        known_components=known_components,
        before=before,
        after=after,
    )


def _validate_new_stage(
    run: WorkflowRun,
    stage_id: str,
    component: str,
    known_components: frozenset[str],
) -> None:
    if not stage_id:
        raise WorkflowContractError("stage id must be non-empty")
    if any(stage.id == stage_id for stage in run.stages):
        raise WorkflowContractError(f"duplicate stage id: {stage_id}")
    _require_component(component, known_components)


def _require_component(component: str, known_components: frozenset[str]) -> None:
    if component not in known_components:
        raise WorkflowContractError(f"unknown component: {component}")


def _stage_index(run: WorkflowRun, stage_id: str) -> int:
    try:
        return next(
            index for index, stage in enumerate(run.stages) if stage.id == stage_id
        )
    except StopIteration as error:
        raise WorkflowContractError(f"unknown stage id: {stage_id}") from error


def _insertion_index(run: WorkflowRun, *, before: str | None, after: str | None) -> int:
    if (before is None) == (after is None):
        raise WorkflowContractError("exactly one of before or after is required")
    if before is not None:
        return _stage_index(run, before)
    assert after is not None
    return _stage_index(run, after) + 1


def workflow_run_to_dict(run: WorkflowRun) -> dict[str, Any]:
    return {
        "version": 1,
        "run_id": str(run.run_id),
        "workflow": run.workflow,
        "root": str(run.root),
        "change": run.change,
        "stages": [
            {
                "id": stage.id,
                "component": stage.component,
                "status": stage.status,
                "result": stage.result,
            }
            for stage in run.stages
        ],
        "observed_bundle": (
            str(run.observed_bundle) if run.observed_bundle is not None else None
        ),
    }
