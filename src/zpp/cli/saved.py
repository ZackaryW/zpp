from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import run_domain
from zpp.core.state import create_saved, list_saved, remove_saved


saved_app = typer.Typer(help="Manage saved override layers.")


@saved_app.command("create")
def saved_create(name: str, target: Path) -> None:
    run_domain(lambda: create_saved(Path.home(), name, target))


@saved_app.command("list")
def saved_list() -> None:
    def action() -> None:
        for name, target in list_saved(Path.home()):
            typer.echo(f"{name}\t{target}")

    run_domain(action)


@saved_app.command("remove")
def saved_remove(
    name: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    if not yes and not typer.confirm(f"Remove saved layer {name}?"):
        return
    run_domain(lambda: remove_saved(Path.home(), name))
