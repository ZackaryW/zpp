from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp import __version__
from zpp.cli.behavior import behave
from zpp.cli.initialization import initialize
from zpp.cli.resolution import resolve
from zpp.cli.shared import Runtime
from zpp.cli.traits import app as trait_app
from zpp.cli.workflow import app as workflow_app

app = typer.Typer(
    name="zpp",
    help="Resolve repository-oriented workflow traits for coding agents.",
    no_args_is_help=True,
)
app.command("init")(initialize)
app.command("resolve")(resolve)
app.command("behave")(behave)
app.add_typer(trait_app, name="trait")
app.add_typer(workflow_app, name="workflow")


def _version(value: bool) -> None:
    if value:
        typer.echo(f"ZPP version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version, is_eager=True),
    ] = False,
    path: Annotated[
        Path | None,
        typer.Option(
            "--path",
            help="OpenLease state root for invocation-scoped trait bindings.",
        ),
    ] = None,
) -> None:
    """Select the state root used by OpenLease-backed commands."""
    del version
    ctx.obj = Runtime(
        (path if path is not None else Path.home() / ".openlease").resolve()
    )
