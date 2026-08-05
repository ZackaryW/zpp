from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import AgentOption, interactive_terminal_available, run_domain
from zpp.core.agents import as_agent_names
from zpp.core.skills import SkillLifecycleReport, manage_workflow_skills
from zpp.utils.agent_selection import select_agents
from zpp.utils.models import CancelledAgentSelection


workflow_app = typer.Typer(help="Manage ZPP's standard workflow bundle.")


@workflow_app.command("install")
def workflow_install(
    target: Annotated[Path | None, typer.Argument()] = None,
    global_: Annotated[bool, typer.Option("--global")] = False,
    agent: Annotated[
        list[AgentOption] | None,
        typer.Option("--agent", help="Install for a supported agent application."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Install locally despite a compatible global bundle."),
    ] = False,
    with_openspec: Annotated[
        bool,
        typer.Option(
            "--with-openspec",
            help="Also bootstrap repository-local OpenSpec operation skills.",
        ),
    ] = False,
) -> None:
    _run_workflow_command(
        "install",
        target,
        global_,
        agent,
        force=force,
        bootstrap_openspec=with_openspec,
    )


@workflow_app.command("update")
def workflow_update(
    target: Annotated[Path | None, typer.Argument()] = None,
    global_: Annotated[bool, typer.Option("--global")] = False,
    agent: Annotated[
        list[AgentOption] | None,
        typer.Option("--agent", help="Update for a supported agent application."),
    ] = None,
) -> None:
    _run_workflow_command("update", target, global_, agent)


@workflow_app.command("remove")
def workflow_remove(
    target: Annotated[Path | None, typer.Argument()] = None,
    global_: Annotated[bool, typer.Option("--global")] = False,
    agent: Annotated[
        list[AgentOption] | None,
        typer.Option("--agent", help="Remove for a supported agent application."),
    ] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    selected = _workflow_agents(agent)
    if not selected:
        return
    if not yes and not typer.confirm("Remove the selected managed standard workflow bundle?"):
        return
    _execute_workflow_command("remove", target, global_, selected)


def _run_workflow_command(
    operation: str,
    target: Path | None,
    global_: bool,
    agent: list[AgentOption] | None,
    *,
    force: bool = False,
    bootstrap_openspec: bool = False,
) -> None:
    selected = _workflow_agents(agent)
    if not selected:
        return
    _execute_workflow_command(
        operation,
        target,
        global_,
        selected,
        force=force,
        bootstrap_openspec=bootstrap_openspec,
    )


def _execute_workflow_command(
    operation: str,
    target: Path | None,
    global_: bool,
    selected: tuple[str, ...],
    *,
    force: bool = False,
    bootstrap_openspec: bool = False,
) -> None:
    if global_ and target is not None:
        raise typer.BadParameter("--global does not accept a local target")

    def action() -> None:
        report = manage_workflow_skills(
            home=Path.home(),
            current_directory=Path.cwd(),
            target=target,
            scope="global" if global_ else "local",
            agents=as_agent_names(selected),
            operation=operation,  # type: ignore[arg-type]
            force=force,
            bootstrap_openspec=bootstrap_openspec,
        )
        _emit_workflow_report(report)

    run_domain(action)


def _workflow_agents(agent: list[AgentOption] | None) -> tuple[str, ...]:
    selected = tuple(item.value for item in agent or ())
    if selected:
        return selected
    if not interactive_terminal_available():
        raise typer.BadParameter("workflow lifecycle commands require --agent when noninteractive")
    selection = select_agents(("pi", "codex", "claude"))
    if isinstance(selection, CancelledAgentSelection):
        typer.echo("Agent selection cancelled.", err=True)
        raise typer.Exit(1)
    return selection.agents


def _emit_workflow_report(report: SkillLifecycleReport) -> None:
    for action in report.actions:
        if action == "skip-global":
            typer.echo("Compatible global workflow skills reused; local installation skipped.")
    for agents in report.coexisting_agents:
        typer.echo(
            "Managed workflow skills coexist in global and local scopes for "
            f"{', '.join(agents)}; no scope precedence selected."
        )
    for difference in report.differences:
        agents = ", ".join(difference.agents)
        typer.echo(
            "Managed workflow skill versions differ for "
            f"{agents}: global {difference.global_version}, "
            f"local {difference.local_version}; no scope precedence selected."
        )
