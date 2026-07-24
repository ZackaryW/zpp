"""Governance reader/writer lease commands."""

from pathlib import Path

import typer

from ..core import leases
from .common import emit, fail


app = typer.Typer(no_args_is_help=True, help=__doc__)


def _human(data: dict) -> None:
    typer.echo(f"{data.get('state', 'ok')}  {data.get('key', {}).get('branch', '')}")


@app.command("status")
def lease_status(
    root: Path,
    branch: str,
    as_json: bool = typer.Option(False, "--json"),
):
    emit(leases.status(root, branch), as_json, _human)


@app.command("acquire")
def lease_acquire(
    root: Path,
    branch: str,
    mode: str = typer.Option(..., help="read or write"),
    session: str = typer.Option(..., help="opaque agent session id"),
    ttl: int = typer.Option(300, help="renewal lifetime in seconds"),
    as_json: bool = typer.Option(False, "--json"),
):
    try:
        result = leases.acquire(root, branch, mode, session, ttl_seconds=ttl)
    except leases.LeaseError as exc:
        fail(str(exc))
    emit(result, as_json, _human)


@app.command("renew")
def lease_renew(
    root: Path,
    branch: str,
    session: str = typer.Option(...),
    ttl: int = typer.Option(300),
    as_json: bool = typer.Option(False, "--json"),
):
    try:
        result = leases.renew(root, branch, session, ttl_seconds=ttl)
    except leases.LeaseError as exc:
        fail(str(exc))
    emit(result, as_json, _human)


@app.command("release")
def lease_release(
    root: Path,
    branch: str,
    session: str = typer.Option(...),
    as_json: bool = typer.Option(False, "--json"),
):
    try:
        result = leases.release(root, branch, session)
    except leases.LeaseError as exc:
        fail(str(exc))
    emit(result, as_json, _human)


@app.command("recover")
def lease_recover(
    root: Path,
    branch: str,
    yes: bool = typer.Option(False, "--yes", help="explicitly clear stale holders"),
    as_json: bool = typer.Option(False, "--json"),
):
    try:
        result = leases.recover_stale(root, branch, confirm=yes)
    except leases.LeaseError as exc:
        fail(str(exc))
    emit(result, as_json, _human)
