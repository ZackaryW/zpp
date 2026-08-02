from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import run_domain
from zpp.core.state import copy_profile, create_profile, list_profiles, remove_profile


profile_app = typer.Typer(help="Manage user profiles and saved override layers.")


@profile_app.command("create")
def profile_create(name: str) -> None:
    run_domain(lambda: create_profile(Path.home(), name))


@profile_app.command("list")
def profile_list() -> None:
    def action() -> None:
        for name in list_profiles(Path.home()):
            typer.echo(name)

    run_domain(action)


@profile_app.command("remove")
def profile_remove(
    name: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    if not yes and not typer.confirm(f"Remove profile {name}?"):
        return
    run_domain(lambda: remove_profile(Path.home(), name))


@profile_app.command("copy")
def profile_copy(source: str, destination: str) -> None:
    run_domain(lambda: copy_profile(Path.home(), source, destination))
