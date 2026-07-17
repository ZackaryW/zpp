"""zpp snapshot - local undo of zpp-owned state."""

import typer

from ..core import snapshot as snapshots
from .common import emit, fail, only_workset

app = typer.Typer(no_args_is_help=True, help="Local undo of zpp-owned state")


@app.command()
def take(name: str = typer.Argument(None), note: str = typer.Option(None)):
    """Manual snapshot of zpp-owned state."""
    name = name or only_workset()
    snap_id = snapshots.take(name, "manual", note)
    if snap_id is None:
        fail(f"no sidecar for '{name}' - nothing to snapshot")
    typer.echo(snap_id)


@app.command("list")
def snapshot_list(name: str = typer.Argument(None), as_json: bool = typer.Option(False, "--json")):
    """Snapshots with timestamps and trigger provenance."""
    name = name or only_workset()
    rows = snapshots.list_snapshots(name)
    emit(rows, as_json, lambda rows: [
        typer.echo(f"{r['id']}  trigger={r.get('trigger', '?')}"
                   + (f"  note={r['note']}" if r.get("note") else ""))
        for r in rows
    ] or typer.echo("no snapshots"))


@app.command()
def restore(
    snap_id: str,
    name: str = typer.Argument(None),
    workspace_file: bool = typer.Option(False, "--workspace-file", help="also write back the user-owned .code-workspace"),
):
    """Rewrite zpp-owned files from a snapshot (workspace file only on --workspace-file)."""
    name = name or only_workset()
    try:
        written = snapshots.restore(name, snap_id, workspace_file)
    except FileNotFoundError as e:
        fail(str(e))
    for path in written:
        typer.echo(f"restored {path}")
