"""Public workflow reminder commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer

from zpp.artifacts import (
    packaged_component_contracts,
    packaged_workflow_contracts,
)
from zpp.cli.shared import emit_json, runtime, user_action
from zpp.core.workflows import (
    WorkflowCheck,
    WorkflowRun,
    WorkflowStageState,
    check_workflow_run,
    delete_workflow_stage,
    first_pending_stage,
    insert_workflow_stage,
    modify_workflow_stage,
    record_workflow_result,
    upsert_workflow_stage,
)
from zpp.utils.workflow_reminders import WorkflowReminderRepository

app = typer.Typer(
    help="Manage target-scoped workflow reminder runs.",
    no_args_is_help=True,
)
stage_app = typer.Typer(
    help="Directly customize one active reminder checklist.",
    no_args_is_help=True,
)
app.add_typer(stage_app, name="stage")

SUCCESS_RESULTS = frozenset(
    {"completed", "skipped", "not-applicable", "already-completed"}
)


def _repository(ctx: typer.Context) -> WorkflowReminderRepository:
    components = packaged_component_contracts()
    return WorkflowReminderRepository(
        runtime(ctx).home,
        known_components=frozenset(item.name for item in components),
    )


def _workflow(name: str):
    contracts = {item.name: item for item in packaged_workflow_contracts()}
    try:
        return contracts[name]
    except KeyError as error:
        raise typer.BadParameter(
            f"unknown complete workflow: {name}", param_hint="workflow"
        ) from error


def _component(name: str):
    contracts = {item.name: item for item in packaged_component_contracts()}
    try:
        return contracts[name]
    except KeyError as error:
        raise typer.BadParameter(
            f"unknown workflow component: {name}", param_hint="--component"
        ) from error


def _stage_payload(stage: WorkflowStageState | None) -> dict[str, object] | None:
    if stage is None:
        return None
    return {
        "id": stage.id,
        "component": stage.component,
        "status": stage.status,
        "result": stage.result,
    }


def _run_payload(run: WorkflowRun) -> dict[str, object]:
    return {
        "run_id": str(run.run_id),
        "workflow": run.workflow,
        "root": str(run.root),
        "change": run.change,
        "stages": [_stage_payload(stage) for stage in run.stages],
        "next_stage": _stage_payload(first_pending_stage(run)),
        "bundle": str(run.observed_bundle) if run.observed_bundle else None,
    }


def _check_payload(check: WorkflowCheck) -> dict[str, object]:
    return {
        "status": check.status,
        "tracking": check.status,
        "allowed": check.allowed,
        "sequence_match": check.sequence_match,
        "workflow": check.workflow,
        "expected_stage": _stage_payload(check.expected_stage),
        "unfinished_stages": [
            _stage_payload(stage) for stage in check.unfinished_stages
        ],
        "warning": check.warning,
    }


def _stored(ctx: typer.Context, root: Path, change: str):
    stored = user_action(lambda: _repository(ctx).load(root=root, change=change))
    if stored is None:
        raise typer.BadParameter(
            f"no active workflow reminder for root={root.resolve()} change={change}"
        )
    return stored


@app.command("start")
def start(
    ctx: typer.Context,
    workflow: str,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
) -> None:
    """Start or idempotently resume one packaged workflow reminder."""
    stored = user_action(
        lambda: _repository(ctx).start(
            _workflow(workflow),
            root=root,
            change=change,
        )
    )
    emit_json(_run_payload(stored.run))


@app.command("status")
def status(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
) -> None:
    """Inspect one exact active workflow reminder."""
    emit_json(_run_payload(_stored(ctx, root, change).run))


@app.command("stop")
def stop(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
) -> None:
    """Stop one reminder without changing Bundler state."""
    stopped = user_action(lambda: _repository(ctx).stop(root=root, change=change))
    emit_json({"stopped": stopped, "root": str(root.resolve()), "change": change})


@app.command("check")
def check(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    component: Annotated[str, typer.Option("--component")],
    workflow: Annotated[str | None, typer.Option("--workflow")] = None,
) -> None:
    """Compare one caller-selected component with the active reminder."""
    _component(component)
    if workflow is not None:
        _workflow(workflow)
    stored = user_action(lambda: _repository(ctx).load(root=root, change=change))
    result = check_workflow_run(
        stored.run if stored else None,
        component=component,
        workflow=workflow,
    )
    emit_json(_check_payload(result))


@app.command("record")
def record(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    component: Annotated[str, typer.Option("--component")],
    result: Annotated[str, typer.Option("--result")],
    bundle: Annotated[UUID | None, typer.Option("--bundle")] = None,
) -> None:
    """Record one accepted matching component result."""
    contract = _component(component)
    if result not in contract.results:
        raise typer.BadParameter(
            f"result {result!r} is outside {component!r} result vocabulary",
            param_hint="--result",
        )
    stored = _stored(ctx, root, change)
    candidate = record_workflow_result(
        stored.run,
        component=component,
        result=result,
        accepted_results=frozenset(contract.results) & SUCCESS_RESULTS,
        observed_bundle=bundle,
    )
    saved = (
        stored
        if candidate == stored.run
        else user_action(lambda: _repository(ctx).save(stored, candidate))
    )
    emit_json(_run_payload(saved.run))


def _position(before: str | None, after: str | None) -> tuple[str | None, str | None]:
    if (before is None) == (after is None):
        raise typer.BadParameter("supply exactly one of --before or --after")
    return before, after


@stage_app.command("insert")
def insert_stage(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    stage_id: Annotated[str, typer.Option("--id")],
    component: Annotated[str, typer.Option("--component")],
    before: Annotated[str | None, typer.Option("--before")] = None,
    after: Annotated[str | None, typer.Option("--after")] = None,
) -> None:
    """Insert one new component stage."""
    known = frozenset(item.name for item in packaged_component_contracts())
    stored = _stored(ctx, root, change)
    selected_before, selected_after = _position(before, after)
    candidate = user_action(
        lambda: insert_workflow_stage(
            stored.run,
            stage_id=stage_id,
            component=component,
            known_components=known,
            before=selected_before,
            after=selected_after,
        )
    )
    emit_json(_run_payload(_repository(ctx).save(stored, candidate).run))


@stage_app.command("delete")
def delete_stage(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    stage_id: Annotated[str, typer.Option("--id")],
) -> None:
    """Delete one reminder stage."""
    stored = _stored(ctx, root, change)
    candidate = user_action(
        lambda: delete_workflow_stage(stored.run, stage_id=stage_id)
    )
    emit_json(_run_payload(_repository(ctx).save(stored, candidate).run))


@stage_app.command("modify")
def modify_stage(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    stage_id: Annotated[str, typer.Option("--id")],
    component: Annotated[str, typer.Option("--component")],
) -> None:
    """Change one existing reminder stage component."""
    known = frozenset(item.name for item in packaged_component_contracts())
    stored = _stored(ctx, root, change)
    candidate = user_action(
        lambda: modify_workflow_stage(
            stored.run,
            stage_id=stage_id,
            component=component,
            known_components=known,
        )
    )
    emit_json(_run_payload(_repository(ctx).save(stored, candidate).run))


@stage_app.command("upsert")
def upsert_stage(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option("--root")],
    change: Annotated[str, typer.Option("--change")],
    stage_id: Annotated[str, typer.Option("--id")],
    component: Annotated[str, typer.Option("--component")],
    before: Annotated[str | None, typer.Option("--before")] = None,
    after: Annotated[str | None, typer.Option("--after")] = None,
) -> None:
    """Idempotently create or modify one reminder stage."""
    known = frozenset(item.name for item in packaged_component_contracts())
    stored = _stored(ctx, root, change)
    if not any(stage.id == stage_id for stage in stored.run.stages):
        selected_before, selected_after = _position(before, after)
    else:
        selected_before, selected_after = before, after
    candidate = user_action(
        lambda: upsert_workflow_stage(
            stored.run,
            stage_id=stage_id,
            component=component,
            known_components=known,
            before=selected_before,
            after=selected_after,
        )
    )
    saved = (
        stored
        if candidate == stored.run
        else user_action(lambda: _repository(ctx).save(stored, candidate))
    )
    emit_json(_run_payload(saved.run))


@app.command("remind")
def remind(
    ctx: typer.Context,
    root: Annotated[Path, typer.Argument()] = Path("."),
) -> None:
    """Emit compact prompt context for active reminders, or stay silent."""
    runs = user_action(lambda: _repository(ctx).list_for_root(root=root))
    for stored in runs:
        pending = first_pending_stage(stored.run)
        if pending is None:
            continue
        remaining = sum(stage.status == "pending" for stage in stored.run.stages)
        typer.echo(
            f"workflow={stored.run.workflow} change={stored.run.change} "
            f"next={pending.id} component={pending.component} remaining={remaining}"
        )
