from __future__ import annotations

import typer

from zpp.cli.shared import runtime, user_action
from zpp.utils.native_open import open_directory


def open_home(ctx: typer.Context) -> None:
    """Create and open the selected ZPP home."""
    home = runtime(ctx).home
    if home.path.is_symlink():
        raise typer.BadParameter("selected ZPP home cannot be a symlink")
    user_action(lambda: home.path.mkdir(parents=True, exist_ok=True))
    user_action(lambda: open_directory(home.path))
    typer.echo(str(home.path))
