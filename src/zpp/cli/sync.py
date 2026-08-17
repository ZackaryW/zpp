from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent

from zpp.cli.lifecycle import generated_entries, packaged_entries
from zpp.cli.shared import (
    abort_cancelled,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    user_action,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents
from zpp.utils.lifecycle import (
    SelectedProjection,
    inspect_entries,
    installed_agents,
    select_projections,
)
from zpp.utils.openspec import generated_openspec_skill_sets


def sync(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Synchronize one or more supported agents."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Reproject owned integrations regardless of drift.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Emit the complete synchronization report as JSON.",
        ),
    ] = False,
) -> None:
    """Bring installed ZPP integrations up to par with the packaged assets."""
    try:
        selection = select_many_agents(
            tuple(agent or ()),
            required=False,
            interactive=interactive_terminal(),
            prompt=prompt_agent_selection,
        )
    except AgentSelectionError as error:
        raise typer.BadParameter(str(error), param_hint="--agent") from error
    if selection.cancelled:
        abort_cancelled()

    root = Path.cwd().resolve()
    report = user_action(lambda: _synchronize(selection.agents, root, force=force))
    if json_output:
        emit_json(report)
        return
    typer.echo(_sync_summary(report))


def _synchronize(
    agents: Sequence[Agent],
    root: Path,
    *,
    force: bool,
) -> list[dict[str, object]]:
    packaged = packaged_entries(agents, target=root)
    inspected = inspect_entries(packaged)
    installed = installed_agents(inspected)

    records: list[dict[str, object]] = [
        {
            "agent": agent.value,
            "asset": "-",
            "status": "uninitialized",
            "decision": "skip",
        }
        for agent in agents
        if agent.value not in installed
    ]
    if not installed:
        return records

    ready = tuple(agent for agent in agents if agent.value in installed)
    scoped = tuple(item for item in inspected if item.entry.agent in installed)
    records.extend(_apply(select_projections(scoped, force=force)))

    with generated_openspec_skill_sets(ready, cwd=root) as generated:
        entries = generated_entries(generated, target=root)
        selected = select_projections(inspect_entries(entries), force=force)
        records.extend(_apply(selected))
    return records


def _apply(
    selected: Sequence[SelectedProjection],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in selected:
        record = item.to_dict()
        operation = {
            "project": item.entry.project,
            "reproject": item.entry.reproject,
        }.get(item.decision)
        if operation is not None:
            try:
                record["status"] = operation().status
            except Exception as error:
                record["status"] = "projection-failed"
                record["error"] = str(error)
        records.append(record)
    return records


def _sync_summary(records: Sequence[dict[str, object]]) -> str:
    decisions = [str(record.get("decision", "")) for record in records]
    projected = sum(decision in {"project", "reproject"} for decision in decisions)
    repaired = sum(decision == "reproject" for decision in decisions)
    current = sum(decision == "current" for decision in decisions)
    conflicted = sum(decision == "conflict" for decision in decisions)
    preserved = sum(decision == "preserve" for decision in decisions)
    uninitialized = sum(decision == "skip" for decision in decisions)
    failed = sum(
        str(record.get("status", "")) == "projection-failed" for record in records
    )
    parts = [f"{projected} reprojected", f"{current} already current"]
    if repaired:
        parts.append(f"{repaired} repaired")
    if conflicted:
        parts.append(f"{conflicted} modified (use --force)")
    if preserved:
        parts.append(f"{preserved} preserved")
    if uninitialized:
        parts.append(f"{uninitialized} uninitialized")
    if failed:
        parts.append(f"{failed} failed")
    return "Synchronized: " + ", ".join(parts) + "."


__all__ = ["sync"]
