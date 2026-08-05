from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import run_domain
from zpp.core.behavior import execute_behavior, initialize_behavior


def behavior_command(
    command: Annotated[str, typer.Argument(help="Command name or 'init'.")],
    all_: Annotated[
        bool,
        typer.Option("--all", help="Select every target declared by the command."),
    ] = False,
    base: Annotated[
        str | None,
        typer.Option("--base", help="Exact base revision for affected selection."),
    ] = None,
    head: Annotated[
        str | None,
        typer.Option("--head", help="Exact head revision for affected selection."),
    ] = None,
) -> None:
    """Run repository-owned affected verification."""
    if command == "init":
        if all_ or base is not None or head is not None:
            raise typer.BadParameter("behavior init does not accept selection options")
        report = run_domain(lambda: initialize_behavior(Path.cwd()))
        if report is None:
            return
        typer.echo(
            f"Behavior mapping {'created' if report.created else 'validated'}: "
            f"{report.root / 'zpp.behave.yaml'}"
        )
        if report.nx_executable is None:
            typer.echo("Nx unavailable; provider-neutral commands remain supported.")
        elif report.nx_surface is None:
            typer.echo(
                f"Nx found at {report.nx_executable}, but its workspace surface "
                f"is unavailable: {report.nx_diagnostic}"
            )
        else:
            typer.echo(
                f"Nx available at {report.nx_executable}; "
                f"discovered {len(report.nx_surface.projects)} projects."
            )
            for project, targets in report.nx_surface.projects.items():
                typer.echo(
                    f"  {project}: {', '.join(sorted(targets)) or '(no targets)'}"
                )
        return

    report = run_domain(
        lambda: execute_behavior(
            Path.cwd(), command, complete=all_, base=base, head=head
        )
    )
    if report is None:
        return
    if report.result is None:
        typer.echo(f"No targets are affected for behavior command {command}.")
        return
    if report.result.stdout:
        typer.echo(report.result.stdout, nl=not report.result.stdout.endswith("\n"))
    if report.result.stderr:
        typer.echo(
            report.result.stderr,
            err=True,
            nl=not report.result.stderr.endswith("\n"),
        )
    if report.result.returncode:
        raise typer.Exit(report.result.returncode)
