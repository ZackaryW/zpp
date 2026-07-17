"""zpp config - layered pva config."""

import json
from pathlib import Path

import typer

from ..core import governance
from .common import flatten

app = typer.Typer(no_args_is_help=True, help="Layered pva config")


@app.command("resolve")
def config_resolve(
    path: Path = typer.Argument(Path(".")),
    as_json: bool = typer.Option(False, "--json"),
    sources: bool = typer.Option(False, help="show which layer supplied each value"),
):
    """Effective config: repo zpp.toml -> workset overlay -> store defaults."""
    result = governance.resolve_config(path)
    if as_json:
        typer.echo(json.dumps(result if sources else result["effective"], indent=2))
        return
    for key, value in sorted(flatten(result["effective"]).items()):
        origin = f"  ({result['origins'].get(key, '?')})" if sources else ""
        typer.echo(f"{key} = {value!r}{origin}")
