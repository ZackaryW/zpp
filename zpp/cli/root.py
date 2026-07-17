"""Root commands: resolve, bootstrap, doctor."""

from pathlib import Path

import typer

from ..core import governance, toolchain
from .common import emit


def resolve(path: Path = typer.Argument(Path(".")), as_json: bool = typer.Option(False, "--json")):
    """Governance mode of a directory: which of the 4 rules matched."""
    result = governance.resolve(path)

    def human(r):
        line = f"{r['mode']}"
        if r["rule"]:
            line += f"  (rule {r['rule']})"
        if r.get("store"):
            line += f"  store={r['store']} [{r.get('binding')}]"
        if r.get("root"):
            line += f"  root={r['root']}"
        typer.echo(line)
        for w in r["warnings"]:
            typer.secho(f"warning: {w}", fg="yellow")

    emit(result, as_json, human)


def bootstrap(dry_run: bool = typer.Option(False, "--dry-run", help="show what would install")):
    """Install the governance toolchain (idempotent; uv is the one prerequisite)."""
    installed, manual = toolchain.bootstrap(dry_run)
    for item in installed:
        typer.echo(f"installed: {item}")
    if not installed and not manual:
        typer.echo("toolchain complete - nothing to install")
    for item in manual:
        typer.secho(f"manual step: {item}", fg="yellow")
    if manual:
        raise typer.Exit(2)


def doctor(as_json: bool = typer.Option(False, "--json")):
    """Verify the governance toolchain (detect-only)."""
    report = toolchain.doctor()

    def human(rows):
        for r in rows:
            mark = "✓" if r["present"] else "✗"
            detail = r["version"] or "" if r["present"] else f"missing - {r['hint']}"
            typer.echo(f"{mark} {r['tool']}  {detail}".rstrip())

    emit(report, as_json, human)
    if any(not r["present"] for r in report):
        raise typer.Exit(1)
