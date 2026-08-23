from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent, Scope

from zpp.cli.lifecycle import inspect_installations, reconcile_installations
from zpp.cli.shared import (
    abort_cancelled,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    user_action,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents


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
    inspections = inspect_installations(
        agents,
        target=root,
        scope=Scope.USER,
        project_root=None,
        include_companions=True,
    )
    return reconcile_installations(inspections, force=force, absent="skip")


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
    migrations = [record for record in records if record.get("asset") == "migration"]
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
    for migration in migrations:
        status = migration["status"]
        surviving = ", ".join(migration.get("surviving_obsolete", [])) or "none"
        failures = ", ".join(migration.get("failures", []))
        detail = (
            f"{migration['agent']} migration {status}; surviving obsolete: {surviving}"
        )
        if failures:
            detail += f"; retirement failed: {failures}"
        parts.append(detail)
    return "Synchronized: " + ", ".join(parts) + "."


__all__ = ["sync"]
