from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import run_domain
from zpp.core.resolution import resolve_traits


def resolve_command(
    target: Annotated[Path | None, typer.Argument()] = None,
) -> None:
    def action() -> None:
        output = resolve_traits(Path.home(), target or Path.cwd())
        if output:
            typer.echo(output, nl=False)

    run_domain(action)
