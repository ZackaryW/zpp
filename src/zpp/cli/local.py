from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import run_domain
from zpp.core.state import initialize_local_layer


local_app = typer.Typer(help="Manage repository and subfolder layers.")


@local_app.command("init")
def local_init(
    target: Annotated[Path | None, typer.Argument()] = None,
) -> None:
    run_domain(lambda: initialize_local_layer(target or Path.cwd()))
