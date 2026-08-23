from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Protocol

import typer
from agent_router import Scope

from zpp.cli.lifecycle import SUPPORTED_AGENTS, packaged_entries
from zpp.cli.shared import agent_router, emit_json, runtime, user_action
from zpp.utils.agent_router import remove_workflow_skill
from zpp.utils.lifecycle import LifecycleEntry
from zpp.utils.openspec import OPENSPEC_CORE_SKILL_NAMES
from zpp.utils.product_home import PreparedBundlerState


class _PreparedState(Protocol):
    def replace(self) -> None: ...

    def discard(self) -> None: ...


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
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit the complete reset report as JSON."),
    ] = False,
) -> None:
    """Remove ZPP user integrations and replace managed Bundler state."""
    if not yes:
        raise typer.BadParameter(
            "--yes is required for complete reset",
            param_hint="--yes",
        )
    selected = runtime(ctx).home
    report = user_action(
        lambda: _reset_state(
            reset_projections(),
            prepare=lambda: PreparedBundlerState.prepare(selected),
        )
    )
    if json_output:
        emit_json(report.to_dict())
        return
    typer.echo(_reset_summary(report))


def reset_projections() -> tuple[LifecycleEntry, ...]:
    """Derive reset targets from the shared lifecycle inventory.

    Packaged entries come from the inventory that initialization and
    synchronization also use. The canonical OpenSpec skills are appended per
    agent as removal-only entries, because they are generated rather than
    packaged and reset deletes them by stable name under Agent Router's
    forced-owned deletion contract.
    """
    target = Path.cwd().resolve()
    projections: list[LifecycleEntry] = []
    for agent in SUPPORTED_AGENTS:
        projections.extend(packaged_entries((agent,), target=target))
        router = agent_router(agent, target)
        projections.extend(
            LifecycleEntry(
                agent=agent.value,
                kind=f"skill:{name}",
                inspect=None,
                project=None,
                remove=(
                    lambda selected_router=router, selected_name=name: (
                        remove_workflow_skill(
                            selected_router,
                            selected_name,
                            Scope.USER,
                            None,
                            force=True,
                        )
                    )
                ),
            )
            for name in OPENSPEC_CORE_SKILL_NAMES
        )
    return tuple(projections)


def _reset_state(
    projections: Sequence[LifecycleEntry],
    *,
    prepare: Callable[[], _PreparedState],
) -> _ResetReport:
    inspected: list[tuple[LifecycleEntry, dict[str, object]]] = []
    inspections_by_projection: dict[int, dict[str, object]] = {}
    conflicts: list[dict[str, object]] = []
    for projection in projections:
        if projection.inspect is None:
            continue
        try:
            result = projection.inspect()
            record = _record(projection, result.to_dict())
        except Exception as error:
            record = _record(
                projection,
                {"status": "inspection-failed", "error": str(error)},
            )
        inspected.append((projection, record))
        inspections_by_projection[id(projection)] = record
        if record["status"] not in {"absent", "current"}:
            conflicts.append(record)

    if conflicts:
        raise ValueError("reset preflight failed: " + _summarize(conflicts))

    prepared = prepare()
    removals: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for projection in projections:
        inspection = inspections_by_projection.get(id(projection))
        if inspection is not None and inspection["status"] == "absent":
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
    projection: LifecycleEntry,
    values: Mapping[str, object],
) -> dict[str, object]:
    return {
        **values,
        "agent": projection.agent,
        "asset": projection.kind,
    }


def _reset_summary(report: _ResetReport) -> str:
    removed = sum(record.get("status") == "removed" for record in report.removals)
    absent = sum(
        record.get("status") == "absent"
        for record in (*report.inspections, *report.removals)
    )
    return (
        f"Reset complete: {removed} removed, {absent} already absent; "
        f"Bundler state {report.state}."
    )


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
