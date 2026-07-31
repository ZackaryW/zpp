from __future__ import annotations

from typing import Annotated

import typer

from zpp import __version__
from zpp.cli.global_commands import global_app
from zpp.cli.initialization import init_command
from zpp.cli.local import local_app
from zpp.cli.profile import profile_app
from zpp.cli.resolution import resolve_command
from zpp.cli.saved import saved_app
from zpp.cli.workflow import workflow_app


app = typer.Typer(
    name="zpp",
    help="Zack's Project Protocol.",
    no_args_is_help=True,
)

profile_app.add_typer(saved_app, name="saved")
app.add_typer(profile_app, name="profile")
app.add_typer(global_app, name="global")
app.add_typer(local_app, name="local")
app.add_typer(workflow_app, name="workflow")
app.command("init")(init_command)
app.command("resolve")(resolve_command)


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
