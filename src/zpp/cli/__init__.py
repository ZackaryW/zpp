from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Callable, TypeVar

import typer

from zpp import __version__
from zpp.core.agents import as_agent_names, configure_agents
from zpp.core.errors import ZppDomainError, validation_diagnostic
from zpp.core.resolution import resolve_traits
from zpp.core.skills import SkillLifecycleReport, manage_workflow_skills
from zpp.core.state import (
    create_profile,
    create_saved,
    initialize_local_layer,
    initialize_user_state,
    list_profiles,
    list_saved,
    remove_profile,
    remove_saved,
)
from zpp.utils.agent_selection import select_agents
from zpp.utils.models import (
    CancelledAgentSelection,
    ManagedStateError,
    ZppValidationError,
)


class AgentOption(str, Enum):
    pi = "pi"
    codex = "codex"
    claude = "claude"


app = typer.Typer(
    name="zpp",
    help="Zack's Project Protocol.",
    no_args_is_help=True,
)
profile_app = typer.Typer(help="Manage user profiles and saved override layers.")
saved_app = typer.Typer(help="Manage saved override layers.")
local_app = typer.Typer(help="Manage repository and subfolder layers.")
workflow_app = typer.Typer(help="Manage ZPP's standard workflow bundle.")
app.add_typer(profile_app, name="profile")
profile_app.add_typer(saved_app, name="saved")
app.add_typer(local_app, name="local")
app.add_typer(workflow_app, name="workflow")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"ZPP version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True),
    ] = False,
) -> None:
    """Bootstrap and resolve layered advisory traits."""


@app.command("init")
def init_command(
    agent: Annotated[
        list[AgentOption] | None,
        typer.Option("--agent", help="Configure a global agent lifecycle hook."),
    ] = None,
) -> None:
    def action() -> None:
        home = Path.home()
        initialize_user_state(home)
        selected = tuple(item.value for item in agent or ())
        if not selected and interactive_terminal_available():
            selection = select_agents(("pi", "codex", "claude"))
            if isinstance(selection, CancelledAgentSelection):
                typer.echo("Agent selection cancelled.", err=True)
                raise typer.Exit(1)
            selected = selection.agents
        if selected:
            configure_agents(home, as_agent_names(selected))

    _run_domain(action)


@profile_app.command("create")
def profile_create(name: str) -> None:
    _run_domain(lambda: create_profile(Path.home(), name))


@profile_app.command("list")
def profile_list() -> None:
    def action() -> None:
        for name in list_profiles(Path.home()):
            typer.echo(name)

    _run_domain(action)


@profile_app.command("remove")
def profile_remove(
    name: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    if not yes and not typer.confirm(f"Remove profile {name}?"):
        return
    _run_domain(lambda: remove_profile(Path.home(), name))


@saved_app.command("create")
def saved_create(name: str, target: Path) -> None:
    _run_domain(lambda: create_saved(Path.home(), name, target))


@saved_app.command("list")
def saved_list() -> None:
    def action() -> None:
        for name, target in list_saved(Path.home()):
            typer.echo(f"{name}\t{target}")

    _run_domain(action)


@saved_app.command("remove")
def saved_remove(
    name: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    if not yes and not typer.confirm(f"Remove saved layer {name}?"):
        return
    _run_domain(lambda: remove_saved(Path.home(), name))


@local_app.command("init")
def local_init(
    target: Annotated[Path | None, typer.Argument()] = None,
) -> None:
    _run_domain(lambda: initialize_local_layer(target or Path.cwd()))


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
) -> None:
    _run_workflow_command("install", target, global_, agent, force=force)


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


@app.command("resolve")
def resolve(
    target: Annotated[Path | None, typer.Argument()] = None,
) -> None:
    def action() -> None:
        output = resolve_traits(Path.home(), target or Path.cwd())
        if output:
            typer.echo(output, nl=False)

    _run_domain(action)


def _run_workflow_command(
    operation: str,
    target: Path | None,
    global_: bool,
    agent: list[AgentOption] | None,
    *,
    force: bool = False,
) -> None:
    selected = _workflow_agents(agent)
    if not selected:
        return
    _execute_workflow_command(operation, target, global_, selected, force=force)


def _execute_workflow_command(
    operation: str,
    target: Path | None,
    global_: bool,
    selected: tuple[str, ...],
    *,
    force: bool = False,
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
        )
        _emit_workflow_report(report)

    _run_domain(action)


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


Result = TypeVar("Result")


def interactive_terminal_available() -> bool:
    return sys.stdin.isatty()


def _run_domain(action: Callable[[], Result]) -> Result | None:
    try:
        return action()
    except typer.Exit:
        raise
    except ZppValidationError as error:
        typer.echo(validation_diagnostic(error), err=True)
    except (ZppDomainError, ManagedStateError, OSError, UnicodeError, ValueError) as error:
        typer.echo(str(error), err=True)
    raise typer.Exit(1)
