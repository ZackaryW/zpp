from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer
from openlease.utils.git_adapter import GitAdapter

from zpp.cli.shared import runtime, user_action
from zpp.core.behavior import (
    BehaviorExecutionError,
    BehaviorExecutionReport,
    BehaviorRunInput,
)
from zpp.utils.openlease import OpenLeaseBehaviorDocuments, create_zpp_openlease


def behave(
    ctx: typer.Context,
    command: Annotated[
        str,
        typer.Argument(help="Command name or 'init'.", metavar="COMMAND"),
    ],
    all_: Annotated[
        bool,
        typer.Option("--all", help="Select every target declared by the command."),
    ] = False,
    target: Annotated[
        list[str] | None,
        typer.Option(
            "--target",
            help="Select one declared target identity; repeat for several.",
        ),
    ] = None,
    gate: Annotated[
        str | None,
        typer.Option("--gate", help="Select one configured command-local gate."),
    ] = None,
    base: Annotated[
        str | None,
        typer.Option("--base", help="Exact base revision for affected selection."),
    ] = None,
    head: Annotated[
        str | None,
        typer.Option("--head", help="Exact head revision for affected selection."),
    ] = None,
) -> None:
    """Run repository-owned affected verification through zpp.behave."""
    targets = tuple(target or ())
    revision = base is not None or head is not None
    if command == "init" and (all_ or targets or gate is not None or revision):
        raise typer.BadParameter("behavior init does not accept selection options")
    if sum((all_, bool(targets), gate is not None, revision)) > 1:
        raise typer.BadParameter("behavior selection modes are mutually exclusive")
    if (base is None) != (head is None):
        raise typer.BadParameter("--base and --head must be supplied together")

    root = user_action(lambda: GitAdapter().inspect(Path.cwd()).root)
    path = root / "zpp.behave.yaml"
    existed = path.is_file()
    documents = OpenLeaseBehaviorDocuments(
        create_zpp_openlease(runtime(ctx).state_root)
    )
    if command == "init":
        report = _behavior_action(lambda: documents.initialize(root))
        typer.echo(f"Behavior mapping {'validated' if existed else 'created'}: {path}")
        for diagnostic in report.provider_diagnostics:
            typer.echo(f"  {diagnostic}")
        return

    report = _behavior_action(
        lambda: documents.run(
            root,
            BehaviorRunInput(
                command=command,
                complete=all_,
                base=base,
                head=head,
                targets=targets,
                gate=gate,
            ),
        )
    )
    _emit_execution(report)


def _behavior_action[T](action: Callable[[], T]) -> T:
    try:
        return user_action(action)
    except BehaviorExecutionError as error:
        raise typer.BadParameter(str(error)) from error


def _emit_execution(report: BehaviorExecutionReport) -> None:
    if report.result is None:
        typer.echo(f"No targets are affected for behavior command {report.command}.")
        return
    if report.result.stdout:
        typer.echo(
            report.result.stdout,
            nl=not report.result.stdout.endswith("\n"),
        )
    if report.result.stderr:
        typer.echo(
            report.result.stderr,
            err=True,
            nl=not report.result.stderr.endswith("\n"),
        )
    if report.result.returncode:
        raise typer.Exit(report.result.returncode)
