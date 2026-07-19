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
    if not result["effective"]:
        # Empty is legitimate (no zpp.toml, no profile, no store default), but
        # give the human an on-ramp. JSON stays bare; zpp never authors the file.
        typer.echo("no zpp.toml resolved for this context - author one to "
                   "configure it (see the zpp.toml template in the README)")
        return
    for key, value in sorted(flatten(result["effective"]).items()):
        origin = f"  ({result['origins'].get(key, '?')})" if sources else ""
        typer.echo(f"{key} = {value!r}{origin}")
