"""Shared CLI helpers."""

import json

import typer

from ..core import sidecar


def fail(message: str) -> None:
    typer.secho(f"error: {message}", fg="red", err=True)
    raise typer.Exit(1)


def emit(data, as_json: bool, human) -> None:
    if as_json:
        typer.echo(json.dumps(data, indent=2))
    else:
        human(data)


def only_workset() -> str:
    """The single workset name, when exactly one exists; else demand --workset."""
    names = sidecar.list_names()
    if len(names) != 1:
        fail(f"specify --workset (found: {', '.join(names) or 'none'})")
    return names[0]


def flatten(data: dict, prefix: str = "") -> dict:
    out = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out |= flatten(value, f"{prefix}{key}.")
        else:
            out[f"{prefix}{key}"] = value
    return out
