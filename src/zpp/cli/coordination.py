"""The ZPP-owned coordination command surface."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer
from openlease.result import json_value

from zpp.cli.shared import emit_json, runtime, user_action
from zpp.core.coordination import closure_fingerprint, parse_affected_claim
from zpp.utils.coordination import OpenLeaseCoordination
from zpp.utils.openlease import create_zpp_openlease

app = typer.Typer(
    name="workspace",
    help="Coordinate topology, sessions, blast-surface permits, and disposition.",
    no_args_is_help=True,
)


def _authority() -> typer.models.OptionInfo:
    """A fresh option per command; Typer mutates the instance it is given."""
    return typer.Option(
        "--authorize",
        help="Explicit authority for a destructive operation. Required; no "
        "instruction, trait body, or workflow stage can supply it.",
    )


def _target() -> typer.models.ArgumentInfo:
    return typer.Argument(help="Repository worktree.")


def _coordination(ctx: typer.Context) -> OpenLeaseCoordination:
    return OpenLeaseCoordination(create_zpp_openlease(runtime(ctx).state_root))


def _report(value: object) -> None:
    """Provider records are dataclasses; render them as typed JSON."""
    emit_json(json_value(value))


def _run[T](action: Callable[[], T]) -> T:
    return user_action(action)


@app.command("session")
def session(
    ctx: typer.Context,
    target: Annotated[Path, _target()] = Path("."),
    name: Annotated[
        str | None,
        typer.Option("--session", help="Establish a distinct named session."),
    ] = None,
) -> None:
    """Establish this worktree's session, registering topology if needed."""
    coordination = _coordination(ctx)
    established = _run(lambda: coordination.establish_session(target, name))
    _report(
        {
            "space": established.space_id,
            "session": established.session_identity,
            "repository": established.worktree.repository_id,
            "authority": established.worktree.authority_id,
        }
    )


@app.command("status")
def status(
    ctx: typer.Context,
    space: Annotated[str | None, typer.Option("--space")] = None,
) -> None:
    """Report observed coordination state without changing it."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.status(space)))


@app.command("claim")
def claim(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space", help="Established session.")],
    repository: Annotated[list[str] | None, typer.Option("--repository")] = None,
    authority: Annotated[list[str] | None, typer.Option("--authority")] = None,
) -> None:
    """Declare the blast surface this session intends to affect."""
    coordination = _coordination(ctx)
    declared = parse_affected_claim(tuple(repository or ()), tuple(authority or ()))
    _run(lambda: coordination.declare_claim(space, declared))
    _report(
        {
            "space": space,
            "repositories": list(declared.repository_ids),
            "authorities": list(declared.authority_ids),
        }
    )


@app.command("closure")
def closure(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
) -> None:
    """Expand the declared claim to closure and evaluate lockability."""
    coordination = _coordination(ctx)
    report = _run(lambda: coordination.resolve_closure(space))
    _report(
        {
            "space": space,
            "lockable": report.lockable,
            "authorities": list(report.authority_ids),
            "conflicts": [
                {"authority": item.authority_id, "owner": item.owner_id}
                for item in report.conflicts
            ],
            "blockers": list(report.blockers),
            "promotion_issues": list(report.promotion_issues),
            "fingerprint": closure_fingerprint(report),
        }
    )


@app.command("permit")
def permit(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    fingerprint: Annotated[
        str,
        typer.Option(
            "--fingerprint",
            help="Closure fingerprint reported by closure; the go-ahead is "
            "for that exact closure.",
        ),
    ],
) -> None:
    """Acquire the permit for the exact closure that was reported."""
    coordination = _coordination(ctx)
    grant = _run(lambda: coordination.acquire_permit(space, fingerprint))
    _report({"space": grant.space_id, "authorities": list(grant.authority_ids)})


@app.command("release")
def release(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
) -> None:
    """Release a held permit after verifying the session boundary is safe."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.release_permit(space)))


@app.command("force-release")
def force_release(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    authorize: Annotated[str | None, _authority()] = None,
) -> None:
    """Release a permit that cannot satisfy the boundary check."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.force_release(space, authorize)))


@app.command("relate")
def relate(
    ctx: typer.Context,
    child: Annotated[str, typer.Option("--child")],
    parent: Annotated[str | None, typer.Option("--parent")] = None,
    dependency: Annotated[str | None, typer.Option("--dependency")] = None,
    access: Annotated[str, typer.Option("--access")] = "read_only",
) -> None:
    """Declare the relationship that makes work cross-repository."""
    coordination = _coordination(ctx)
    if (parent is None) == (dependency is None):
        raise typer.BadParameter("declare exactly one of --parent or --dependency")
    if parent is not None:
        _report(_run(lambda: coordination.declare_parent(child, parent)))
        return
    _report(_run(lambda: coordination.declare_dependency(child, dependency, access)))


@app.command("reconcile")
def reconcile(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    repository: Annotated[str, typer.Option("--repository")],
    apply: Annotated[
        bool, typer.Option("--apply", help="Apply the plan instead of reporting it.")
    ] = False,
) -> None:
    """Plan a reconciliation path, or apply exactly one authorized path."""
    coordination = _coordination(ctx)
    if apply:
        _report(_run(lambda: coordination.reconcile_apply(space, repository)))
        return
    _report(_run(lambda: coordination.reconcile_plan(space, repository)))


@app.command("finalize")
def finalize(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
) -> None:
    """Finalize a session whose reconciliation debt is settled."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.finalize(space)))


@app.command("handoff")
def handoff(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    disposition: Annotated[str, typer.Option("--disposition")],
    authorize: Annotated[str | None, _authority()] = None,
) -> None:
    """Record the handoff disposition for retained work."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.handoff(space, disposition, authorize)))


@app.command("abandon")
def abandon(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    repository: Annotated[str, typer.Option("--repository")],
    authorize: Annotated[str | None, _authority()] = None,
) -> None:
    """Abandon one member of a session."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.abandon(space, repository, authorize)))


@app.command("cleanup")
def cleanup(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    repository: Annotated[str, typer.Option("--repository")],
    authorize: Annotated[str | None, _authority()] = None,
) -> None:
    """Remove a generated worktree for one member of a session."""
    coordination = _coordination(ctx)
    _report(_run(lambda: coordination.cleanup(space, repository, authorize)))


@app.command("preparation")
def preparation(
    ctx: typer.Context,
    space: Annotated[str, typer.Option("--space")],
    rollback: Annotated[
        bool, typer.Option("--rollback", help="Roll back instead of resuming.")
    ] = False,
    authorize: Annotated[str | None, _authority()] = None,
) -> None:
    """Resume or roll back a failed preparation."""
    coordination = _coordination(ctx)
    if rollback:
        _report(_run(lambda: coordination.preparation_rollback(space, authorize)))
        return
    _report(_run(lambda: coordination.preparation_resume(space)))
