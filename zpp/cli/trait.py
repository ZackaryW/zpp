"""zpp trait - realtime trait queries. No composer, no compiled artifacts."""

import json
from pathlib import Path

import typer

from ..core import governance, sauce, traits
from .common import emit, fail

app = typer.Typer(no_args_is_help=True, help="Realtime trait queries (list/show/effective)")


def _plugin_override(tool: str | None, path: Path) -> Path | None:
    if not tool:
        return None
    ov = (governance.resolve_config(path)["effective"]
          .get("traits", {}).get("plugins", {}).get(tool))
    return Path(ov) if ov else None


@app.command("list")
def trait_list(
    tool: str = typer.Option(None, "--tool", help="also gather this agent surface's plugin traits"),
    path: Path = typer.Argument(Path("."), help="context for the plugins override"),
    as_json: bool = typer.Option(False, "--json"),
):
    """Every available trait with source, shadowing, and version when known."""
    rows = traits.available(tool, _plugin_override(tool, path))
    def human(rows):
        for r in rows:
            mark = "  (shadowed)" if r["shadowed"] else ""
            version = f"  v{r['version']}" if r.get("version") else ""
            origin = f" {r['plugin']}" if r.get("plugin") else ""
            typer.echo(f"{r['name']}  [{r['source']}{origin}]{version}{mark}")
    emit(rows, as_json, human)


@app.command()
def show(
    name: str,
    tool: str = typer.Option(None, "--tool", help="also gather this agent surface's plugin traits"),
    path: Path = typer.Argument(Path("."), help="context for the plugins override"),
):
    """One trait's content (the winning source's copy)."""
    text = traits.content(name, tool, _plugin_override(tool, path))
    if text is None:
        fail(f"unknown trait '{name}'")
    typer.echo(text, nl=False)


@app.command()
def fetch(ref: str, path: Path = typer.Argument(Path("."))):
    """Fetch/update a remote trait pack via saucepan (managed mode by default)."""
    mode = (governance.resolve_config(path)["effective"]
            .get("traits", {}).get("saucepan", "managed"))
    try:
        binary, fetched = sauce.ensure_binary(mode)
        if fetched:
            typer.echo(f"fetching saucepan release binary -> {binary}")
        sauce.install(binary, ref)
    except sauce.SauceError as e:
        fail(str(e))
    typer.echo(f"installed pack '{ref}'")


@app.command()
def effective(
    path: Path = typer.Argument(Path(".")),
    tool: str = typer.Option(None, "--tool", help="also gather this agent surface's plugin traits"),
    as_json: bool = typer.Option(False, "--json"),
):
    """The applied trait set for a context, concatenated in application order."""
    result = traits.effective(path, tool)
    for name in result["unknown"]:
        typer.secho(f"warning: unknown trait '{name}' - skipped", fg="yellow", err=False)
    if as_json:
        typer.echo(json.dumps(result, indent=2))
        return
    for item in result["applied"]:
        typer.echo(f"<!-- trait: {item['name']} [{item['source']}] -->")
        typer.echo(item["content"])
