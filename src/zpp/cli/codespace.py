from __future__ import annotations

import json
from pathlib import Path
import sys
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
    finalize_codespace,
    find_claim,
    find_released,
    guard_codespace_request,
    inspect_codespace_claim,
    lock_codespace,
    open_codespace,
    read_codespaces,
    record_codespace_disposition,
    unlock_codespace,
)
from zpp.utils.codespace_identity import projection_name
from zpp.utils.codespace_targets import explicit_members


codespace_app = typer.Typer(help="Gate concurrent OpenSpec work through explicit codespaces.")


def _confirm_conflicts(error: CodespaceConflictError, yes: bool) -> bool:
    typer.echo(str(error), err=True)
    return yes or typer.confirm("Create isolated worktrees for all conflicts?")


@codespace_app.command("lock")
def lock_command(
    paths: Annotated[list[Path] | None, typer.Argument()] = None,
    workspace: Annotated[Path | None, typer.Option("--workspace")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
) -> None:
    def action() -> None:
        members = explicit_members(
            workspace=workspace,
            paths=tuple(paths or ()),
        )
        if members is None:
            active_id = discover_codespace_view(
                home=Path.home(),
                current_directory=Path.cwd(),
            )
            if active_id is None:
                raise ValueError(
                    "no active codespace or explicit writable targets; "
                    "pass --workspace or paths"
                )
            typer.echo(active_id)
            return
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
            if typer.confirm("Open the prepared codespace?", default=False):
                open_codespace(Path.home(), result.claim)

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
        projection = (
            projection_name(claim.instance_id, claim.projection.generation)
            if claim.projection is not None
            else "-"
        )
        typer.echo(f"{claim.instance_id}\t{projection}")


@codespace_app.command("status")
def status_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
    json_: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    def action() -> None:
        index = read_codespaces(Path.home())
        if identifier is not None and identifier in index.released:
            released = index.released[identifier]
            if json_:
                typer.echo(
                    json.dumps(
                        {"state": "released", "released": released.model_dump(mode="json")},
                        ensure_ascii=False,
                    )
                )
                return
            typer.echo(f"{released.instance_id}\treleased")
            for debt in released.debts:
                typer.echo(
                    f"{debt.effective_path}\t{debt.branch}\t"
                    f"{debt.branch_disposition}"
                )
            return
        claim = find_claim(Path.home(), identifier, Path.cwd())
        current = inspect_codespace_claim(claim)
        if json_:
            typer.echo(
                json.dumps(
                    {
                        "state": "active",
                        "claim": claim.model_dump(mode="json"),
                        "current": current,
                    },
                    ensure_ascii=False,
                )
            )
            return
        typer.echo(f"{claim.instance_id}\tactive")
        for member in current:
            typer.echo(
                f"{member['name']}\t{member['path']}\t"
                f"{member['current_commit']}\tdirty={str(member['dirty']).lower()}"
            )

    run_domain(action)


@codespace_app.command("open")
def open_command(
    identifier: Annotated[str | None, typer.Argument()] = None,
    tool: Annotated[str | None, typer.Option("--tool")] = None,
) -> None:
    def action() -> None:
        home = Path.home()
        code = open_codespace(home, find_claim(home, identifier, Path.cwd()), tool)
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
        home = Path.home()
        code = exec_codespace(
            home,
            find_claim(home, identifier, Path.cwd()),
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
        home = Path.home()
        code = activate_codespace(
            home,
            find_claim(home, identifier, Path.cwd()),
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
        home = Path.home()
        claim = find_claim(home, identifier, Path.cwd())
        if force and not yes and not typer.confirm(
            "Release the abandoned claim while preserving all worktrees?"
        ):
            raise ValueError("forced recovery declined")
        unlock_codespace(home, claim, force=force)

    run_domain(action)


@codespace_app.command("cleanup")
def cleanup_command(
    identifier: Annotated[str, typer.Argument()],
) -> None:
    def action() -> None:
        home = Path.home()
        for path in cleanup_codespace(home, find_released(home, identifier)):
            typer.echo(str(path))

    run_domain(action)


@codespace_app.command("disposition")
def disposition_command(
    identifier: Annotated[str, typer.Argument()],
    checkout_key: Annotated[str, typer.Argument()],
    state: Annotated[str, typer.Option("--state")],
) -> None:
    def action() -> None:
        if state not in {"reconciled", "abandoned"}:
            raise ValueError("disposition state must be reconciled or abandoned")
        record_codespace_disposition(
            Path.home(),
            identifier,
            checkout_key,
            state,
        )

    run_domain(action)


@codespace_app.command("finalize")
def finalize_command(
    identifier: Annotated[str, typer.Argument()],
) -> None:
    run_domain(lambda: finalize_codespace(Path.home(), identifier))


@codespace_app.command("guard", hidden=True)
def guard_command(
    agent: Annotated[str, typer.Option("--agent")],
) -> None:
    def action() -> None:
        if agent not in {"pi", "codex", "claude"}:
            raise ValueError(f"unsupported agent: {agent}")
        try:
            payload = json.loads(sys.stdin.read())
        except json.JSONDecodeError as error:
            raise ValueError("agent guard payload is not valid JSON") from error
        if not isinstance(payload, dict):
            raise ValueError("agent guard payload must be a JSON object")
        output = guard_codespace_request(Path.home(), agent, payload)
        typer.echo(json.dumps(output, ensure_ascii=False))

    run_domain(action)
