from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID, uuid4

import typer

_BYPASS_TOKEN = "_ZPP_BYPASS_TOKEN"
_BYPASS_REASON = "_ZPP_BYPASS_REASON"


@dataclass(frozen=True, slots=True)
class BypassState:
    token: UUID
    reason: str


def bypass_state(environment: Mapping[str, str] | None = None) -> BypassState | None:
    selected = os.environ if environment is None else environment
    raw_token = selected.get(_BYPASS_TOKEN)
    raw_reason = selected.get(_BYPASS_REASON)
    if raw_token is None and raw_reason is None:
        return None
    if raw_token is None or raw_reason is None or not raw_reason.strip():
        raise ValueError("invalid ZPP bypass environment")
    try:
        token = UUID(raw_token)
    except ValueError as error:
        raise ValueError("invalid ZPP bypass token") from error
    if token.version != 4 or str(token) != raw_token:
        raise ValueError("invalid ZPP bypass token")
    return BypassState(token, raw_reason)


def _child_environment(reason: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment[_BYPASS_TOKEN] = str(uuid4())
    environment[_BYPASS_REASON] = reason
    return environment


def bypass(
    ctx: typer.Context,
    reason: Annotated[str, typer.Option("--reason")],
    acknowledge: Annotated[bool, typer.Option("--acknowledge")] = False,
) -> None:
    """Run one explicitly acknowledged child without Bundler coordination."""
    if not acknowledge:
        raise typer.BadParameter("--acknowledge is required for bypass execution")
    if not reason.strip():
        raise typer.BadParameter("--reason must be non-empty")
    command = tuple(ctx.args)
    if not command:
        raise typer.BadParameter("a child command is required after --")
    rendered = subprocess.list2cmdline(command)
    typer.echo(
        "WARNING: ZPP BUNDLER COORDINATION BYPASS ACTIVE\n"
        f"Reason: {reason}\n"
        f"Command: {rendered}",
        err=True,
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_child_environment(reason),
    )
    if completed.stdout:
        typer.echo(completed.stdout, nl=False)
    if completed.stderr:
        typer.echo(completed.stderr, err=True, nl=False)
    raise typer.Exit(completed.returncode)


__all__: Sequence[str] = ("BypassState", "bypass", "bypass_state")
