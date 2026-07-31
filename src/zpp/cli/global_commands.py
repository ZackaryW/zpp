from __future__ import annotations

from pathlib import Path

import typer

from zpp.cli.shared import run_domain
from zpp.core.state import activate_global_profile


global_app = typer.Typer(help="Manage the active global trait layer.")


@global_app.command("activate")
def global_activate(name: str) -> None:
    run_domain(lambda: activate_global_profile(Path.home(), name))
