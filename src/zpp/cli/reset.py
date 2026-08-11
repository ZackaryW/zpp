from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Protocol

import typer
from agent_router import Agent, Scope

from zpp.artifacts import packaged_workflow_hook, packaged_workflow_skill
from zpp.cli.shared import agent_router, emit_json, runtime, user_action
from zpp.utils.agent_router import (
    inspect_workflow_hook,
    inspect_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
)
from zpp.utils.product_home import PreparedOpenLeaseState

SUPPORTED_AGENTS = (Agent.CODEX, Agent.CLAUDE, Agent.PI, Agent.KIMI)


class _RouterResult(Protocol):
    status: str

    def to_dict(self) -> dict[str, object]: ...


class _PreparedState(Protocol):
    def replace(self) -> None: ...

    def discard(self) -> None: ...


@dataclass(frozen=True, slots=True)
class _ResetProjection:
    agent: str
    kind: str
    inspect: Callable[[], _RouterResult]
    remove: Callable[[], _RouterResult]


@dataclass(frozen=True, slots=True)
class _ResetReport:
    inspections: tuple[Mapping[str, object], ...]
    removals: tuple[Mapping[str, object], ...]
    state: str

    def to_dict(self) -> dict[str, object]:
        return {
            "inspections": [dict(item) for item in self.inspections],
            "removals": [dict(item) for item in self.removals],
            "state": self.state,
        }


def reset(
    ctx: typer.Context,
    yes: Annotated[
        bool,
        typer.Option("--yes", help="Confirm complete user integration reset."),
    ] = False,
) -> None:
    """Remove ZPP user integrations and replace managed OpenLease state."""
    if not yes:
        raise typer.BadParameter(
            "--yes is required for complete reset",
            param_hint="--yes",
        )
    selected = runtime(ctx).home
    report = user_action(
        lambda: _reset_state(
            reset_projections(),
            prepare=lambda: PreparedOpenLeaseState.prepare(selected),
        )
    )
    emit_json(report.to_dict())


def reset_projections() -> tuple[_ResetProjection, ...]:
    target = Path.cwd().resolve()
    skill = packaged_workflow_skill()
    projections: list[_ResetProjection] = []
    for agent in SUPPORTED_AGENTS:
        router = agent_router(agent, target)
        hook = packaged_workflow_hook(agent)
        projections.extend(
            (
                _ResetProjection(
                    agent.value,
                    "hook",
                    lambda selected_router=router, selected_hook=hook: (
                        inspect_workflow_hook(
                            selected_router,
                            selected_hook,
                            Scope.USER,
                            None,
                        )
                    ),
                    lambda selected_router=router, selected_hook=hook: (
                        remove_workflow_hook(
                            selected_router,
                            selected_hook.name,
                            Scope.USER,
                            None,
                        )
                    ),
                ),
                _ResetProjection(
                    agent.value,
                    "skill",
                    lambda selected_router=router: inspect_workflow_skill(
                        selected_router,
                        skill,
                        Scope.USER,
                        None,
                    ),
                    lambda selected_router=router: remove_workflow_skill(
                        selected_router,
                        skill.name,
                        Scope.USER,
                        None,
                    ),
                ),
            )
        )
    return tuple(projections)


def _reset_state(
    projections: Sequence[_ResetProjection],
    *,
    prepare: Callable[[], _PreparedState],
) -> _ResetReport:
    inspected: list[tuple[_ResetProjection, dict[str, object]]] = []
    conflicts: list[dict[str, object]] = []
    for projection in projections:
        try:
            result = projection.inspect()
            record = _record(projection, result.to_dict())
        except Exception as error:
            record = _record(
                projection,
                {"status": "inspection-failed", "error": str(error)},
            )
        inspected.append((projection, record))
        if record["status"] not in {"absent", "current"}:
            conflicts.append(record)

    if conflicts:
        raise ValueError("reset preflight failed: " + _summarize(conflicts))

    prepared = prepare()
    removals: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for projection, inspection in inspected:
        if inspection["status"] == "absent":
            continue
        try:
            result = projection.remove()
            record = _record(projection, result.to_dict())
        except Exception as error:
            record = _record(
                projection,
                {"status": "removal-failed", "error": str(error)},
            )
        removals.append(record)
        if record["status"] not in {"absent", "removed"}:
            failures.append(record)

    if failures:
        prepared.discard()
        raise ValueError("reset removal failed: " + _summarize(failures))

    try:
        prepared.replace()
    except Exception:
        prepared.discard()
        raise
    return _ResetReport(
        tuple(record for _, record in inspected),
        tuple(removals),
        "replaced",
    )


def _record(
    projection: _ResetProjection,
    values: Mapping[str, object],
) -> dict[str, object]:
    return {
        **values,
        "agent": projection.agent,
        "asset": projection.kind,
    }


def _summarize(records: Sequence[Mapping[str, object]]) -> str:
    return "; ".join(
        " ".join(
            str(value)
            for value in (
                record["agent"],
                record["asset"],
                record["status"],
                record.get("error", ""),
            )
            if value != ""
        )
        for record in records
    )
