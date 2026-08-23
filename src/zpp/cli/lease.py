from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from openspec_bundler import ChangeMember, LeaseBundle

from zpp.cli.shared import emit_json, runtime, user_action
from zpp.utils.bundler import BundlerLeaseService

app = typer.Typer(
    help="Operate the Bundler lease lifecycle used by zpp-workflow.",
    no_args_is_help=True,
)


def _service(ctx: typer.Context) -> BundlerLeaseService:
    return BundlerLeaseService(runtime(ctx).home)


def _member(value: str) -> tuple[UUID, str]:
    store, separator, change = value.partition(":")
    if not separator or not change.strip():
        raise typer.BadParameter("members must use UUID:CHANGE syntax")
    try:
        return UUID(store), change
    except ValueError as error:
        raise typer.BadParameter(f"invalid store UUID: {store}") from error


def _member_dict(member: ChangeMember) -> dict[str, str]:
    return {"store_uuid": str(member.store_uuid), "change_name": member.change_name}


def _bundle_dict(bundle: LeaseBundle) -> dict[str, object]:
    return {
        "bundle_uuid": str(bundle.bundle_uuid),
        "owner_id": bundle.owner_id,
        "requested_roots": [str(value) for value in bundle.requested_roots],
        "held_stores": [str(value) for value in bundle.held_stores],
        "members": [_member_dict(value) for value in bundle.members],
        "archived_members": [_member_dict(value) for value in bundle.archived_members],
        "topology_digest": bundle.topology_digest,
    }


@app.command("acquire")
def acquire(
    ctx: typer.Context,
    owner: Annotated[str, typer.Option("--owner")],
    member: Annotated[list[str], typer.Option("--member")],
) -> None:
    """Acquire one atomic bundle for exact store/change members."""
    result = user_action(
        lambda: _service(ctx).acquire(owner, tuple(_member(value) for value in member))
    )
    emit_json({"created": result.created, "bundle": _bundle_dict(result.bundle)})


@app.command("status")
def status(ctx: typer.Context) -> None:
    """Inspect retained bundles without changing state."""
    bundles = user_action(lambda: _service(ctx).status())
    emit_json({"bundles": [_bundle_dict(value) for value in bundles]})


@app.command("audit")
def audit(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    path: Annotated[list[Path], typer.Option("--path")],
) -> None:
    """Audit exact changed paths against a retained bundle."""
    result = user_action(lambda: _service(ctx).audit(bundle, path))
    emit_json(
        {
            "ok": result.ok,
            "accepted": [str(value) for value in result.accepted],
            "violations": [str(value) for value in result.violations],
        }
    )
    if not result.ok:
        raise typer.Exit(1)


@app.command("archive")
def archive(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    owner: Annotated[str, typer.Option("--owner")],
    member: Annotated[str, typer.Option("--member")],
) -> None:
    """Record one successfully archived member."""
    updated = user_action(
        lambda: _service(ctx).record_archive(bundle, owner, _member(member))
    )
    emit_json({"bundle": _bundle_dict(updated)})


@app.command("complete")
def complete(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    owner: Annotated[str, typer.Option("--owner")],
) -> None:
    """Release one fully archived bundle."""
    user_action(lambda: _service(ctx).complete(bundle, owner))
    emit_json({"bundle_uuid": str(bundle), "completed": True})


@app.command("abandon")
def abandon(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    owner: Annotated[str, typer.Option("--owner")],
) -> None:
    """Release one retained bundle under its durable owner identity."""
    user_action(lambda: _service(ctx).abandon(bundle, owner))
    emit_json({"bundle_uuid": str(bundle), "abandoned": True})
