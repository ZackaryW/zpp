from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import interactive_terminal_available, run_domain
from zpp.core.codespaces import (
    CodespaceConflictError,
    activate_codespace,
    add_codespace_paths,
    cleanup_codespace,
    discover_codespace_view,
    exec_codespace,
    explicit_members,
    find_claim,
    find_released,
    lock_codespace,
    open_codespace,
    read_codespaces,
    select_workset,
    unlock_codespace,
)


codespace_app = typer.Typer(help="Gate concurrent OpenSpec work through explicit codespaces.")


def _confirm_conflicts(error: CodespaceConflictError, yes: bool) -> bool:
    typer.echo(str(error), err=True)
    return yes or typer.confirm("Create isolated worktrees for all conflicts?")


@codespace_app.command("lock")
def lock_command(
    paths: Annotated[list[Path] | None, typer.Argument()] = None,
    workset: Annotated[str | None, typer.Option("--workset")] = None,
    workspace: Annotated[Path | None, typer.Option("--workspace")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    def action() -> None:
        members = explicit_members(
            workset=workset,
            workspace=workspace,
            paths=tuple(paths or ()),
        )
        if members is None:
            discovery = discover_codespace_view(
                home=Path.home(),
                current_directory=Path.cwd(),
            )
            if discovery.active_id:
                typer.echo(discovery.active_id)
                return
            if len(discovery.candidates) == 1:
                members = discovery.candidates[0].members
            elif len(discovery.candidates) > 1:
                if not interactive_terminal_available():
                    raise ValueError("multiple OpenSpec worksets apply; pass --workset")
                selected = typer.prompt(
                    "OpenSpec workset",
                    default=discovery.candidates[0].name,
                )
                members = select_workset(selected).members
            else:
                raise ValueError(
                    "no active codespace or applicable OpenSpec workset; "
                    "pass --workset, --workspace, or paths"
                )
        try:
            result = lock_codespace(home=Path.home(), members=members, mitigate=False)
        except CodespaceConflictError as error:
            if not _confirm_conflicts(error, yes):
                raise ValueError("codespace mitigation declined") from error
            result = lock_codespace(home=Path.home(), members=members, mitigate=True)
        typer.echo(result.claim.instance_id)
        for name in result.dirty_members:
            typer.echo(f"dirty: {name}", err=True)
        if result.conflicts and interactive_terminal_available():
            if typer.confirm("Open the prepared OpenSpec workset?", default=False):
                open_codespace(result.claim)

    run_domain(action)


@codespace_app.command("add")
def add_command(
    paths: Annotated[list[Path], typer.Argument()],
    codespace: Annotated[str | None, typer.Option("--codespace")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    def action() -> None:
        claim = find_claim(Path.home(), codespace, Path.cwd())
        try:
            replacement = add_codespace_paths(
                home=Path.home(),
                claim=claim,
                paths=paths,
                mitigate=False,
            )
        except CodespaceConflictError as error:
            if not _confirm_conflicts(error, yes):
                raise ValueError("codespace mitigation declined") from error
            replacement = add_codespace_paths(
                home=Path.home(),
                claim=claim,
                paths=paths,
                mitigate=True,
            )
        typer.echo(replacement.instance_id)

    run_domain(action)


@codespace_app.command("list")
def list_command() -> None:
    for claim in read_codespaces(Path.home()).claims.values():
        typer.echo(f"{claim.instance_id}\t{claim.workset_name}")


@codespace_app.command("status")
def status_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
    json_: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    def action() -> None:
        if identifier is not None:
            index = read_codespaces(Path.home())
            claim = index.claims.get(identifier)
            if claim is None and identifier in index.released:
                claim = index.released[identifier].claim
            if claim is None:
                raise ValueError(f"codespace does not exist: {identifier}")
        else:
            claim = find_claim(Path.home(), None, Path.cwd())
        if json_:
            typer.echo(json.dumps(claim.model_dump(mode="json"), ensure_ascii=False))
            return
        typer.echo(f"{claim.instance_id}\t{claim.workset_name}")
        for member in claim.members:
            typer.echo(f"{member.name}\t{member.effective_path}")

    run_domain(action)


@codespace_app.command("open")
def open_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
    tool: Annotated[str | None, typer.Option("--tool")] = None,
) -> None:
    def action() -> None:
        code = open_codespace(find_claim(Path.home(), identifier, Path.cwd()), tool)
        if code:
            raise typer.Exit(code)

    run_domain(action)


@codespace_app.command(
    "exec",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def exec_command(
    context: typer.Context,
    identifier: Annotated[str | None, typer.Option("--codespace")] = None,
) -> None:
    def action() -> None:
        if not context.args:
            raise ValueError("codespace exec requires a command")
        code = exec_codespace(
            Path.home(),
            find_claim(Path.home(), identifier, Path.cwd()),
            context.args,
        )
        if code:
            raise typer.Exit(code)

    run_domain(action)


@codespace_app.command("activate")
def activate_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
) -> None:
    def action() -> None:
        code = activate_codespace(
            Path.home(),
            find_claim(Path.home(), identifier, Path.cwd()),
        )
        if code:
            raise typer.Exit(code)

    run_domain(action)


@codespace_app.command("unlock")
def unlock_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    def action() -> None:
        claim = find_claim(Path.home(), identifier, Path.cwd())
        if force and not yes and not typer.confirm(
            "Release the abandoned claim while preserving all worktrees?"
        ):
            raise ValueError("forced recovery declined")
        unlock_codespace(Path.home(), claim, force=force)

    run_domain(action)


@codespace_app.command("cleanup")
def cleanup_command(
    identifier: Annotated[str, typer.Argument()],
) -> None:
    def action() -> None:
        released = find_released(Path.home(), identifier)
        for path in cleanup_codespace(Path.home(), released):
            typer.echo(str(path))

    run_domain(action)
