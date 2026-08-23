from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer
from openspec_bundler import ChangeMember, LeaseBundle

from zpp.cli.bypass import bypass_state
from zpp.cli.shared import emit_json, runtime, user_action
from zpp.utils.bundler import (
    BundlerLeaseService,
    CoordinatedAcquisition,
    CoordinationTarget,
    WorkflowCoordinationService,
)
from zpp.utils.product_home import WorkflowIdentityRepository

app = typer.Typer(
    help="Operate the Bundler lease lifecycle governed by zpps-workflow-kernel.",
    no_args_is_help=True,
)


def _service(ctx: typer.Context) -> BundlerLeaseService:
    return BundlerLeaseService(runtime(ctx).home)


def _coordination_service(ctx: typer.Context) -> WorkflowCoordinationService:
    return WorkflowCoordinationService(runtime(ctx).home)


def _owner(ctx: typer.Context, supplied: str | None) -> str:
    return supplied or WorkflowIdentityRepository(runtime(ctx).home).resolve()


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


def _input_member_dict(member: tuple[UUID, str]) -> dict[str, str]:
    return {"store_uuid": str(member[0]), "change_name": member[1]}


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


def _coordinated_dict(result: CoordinatedAcquisition) -> dict[str, object]:
    return {
        "coordination": result.coordination,
        "created": result.created,
        "owner_id": result.owner_id,
        "stores": [
            {"id": store.store_id, "root": str(store.root)} for store in result.stores
        ],
        "manifests": [
            {
                "path": str(manifest.path),
                "store_uuid": str(manifest.store_uuid),
                "created": manifest.created,
            }
            for manifest in result.manifests
        ],
        "bundle": _bundle_dict(result.bundle),
    }


def _emit_bypass(operation: str, **evidence: object) -> bool:
    state = user_action(bypass_state)
    if state is None:
        return False
    emit_json(
        {
            "coordination": "bypassed",
            "operation": operation,
            "reason": state.reason,
            **evidence,
        }
    )
    return True


@app.command("acquire")
def acquire(
    ctx: typer.Context,
    owner: Annotated[str | None, typer.Option("--owner")] = None,
    member: Annotated[list[str] | None, typer.Option("--member")] = None,
    root: Annotated[list[Path] | None, typer.Option("--root")] = None,
    change: Annotated[list[str] | None, typer.Option("--change")] = None,
) -> None:
    """Acquire one atomic bundle for exact store/change members."""
    members = tuple(member or ())
    roots = tuple(root or ())
    changes = tuple(change or ())
    if roots or changes:
        if members:
            raise typer.BadParameter("--member cannot be combined with --root/--change")
        if not roots or len(roots) != len(changes):
            raise typer.BadParameter(
                "automatic acquisition requires matching --root and --change options"
            )
        targets = [
            {"root": str(path.resolve()), "change": name}
            for path, name in zip(roots, changes, strict=True)
        ]
        if _emit_bypass("acquire", targets=targets):
            return
        result = user_action(
            lambda: _coordination_service(ctx).acquire(
                tuple(
                    CoordinationTarget(path, name)
                    for path, name in zip(roots, changes, strict=True)
                ),
                override_raw=os.environ.get("ZPP_WORKFLOW_COORDINATION"),
                owner_id=owner,
            )
        )
        emit_json(_coordinated_dict(result))
        return
    if not members:
        raise typer.BadParameter(
            "provide --member or matching --root and --change options"
        )
    parsed_members = tuple(_member(value) for value in members)
    if _emit_bypass(
        "acquire", members=[_input_member_dict(value) for value in parsed_members]
    ):
        return
    result = user_action(
        lambda: _service(ctx).acquire(_owner(ctx, owner), parsed_members)
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
    member: Annotated[str, typer.Option("--member")],
    owner: Annotated[str | None, typer.Option("--owner")] = None,
) -> None:
    """Record one successfully archived member."""
    parsed_member = _member(member)
    if _emit_bypass(
        "archive", bundle_uuid=str(bundle), member=_input_member_dict(parsed_member)
    ):
        return
    updated = user_action(
        lambda: _service(ctx).record_archive(bundle, _owner(ctx, owner), parsed_member)
    )
    emit_json({"bundle": _bundle_dict(updated)})


@app.command("complete")
def complete(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    owner: Annotated[str | None, typer.Option("--owner")] = None,
) -> None:
    """Release one fully archived bundle."""
    if _emit_bypass("complete", bundle_uuid=str(bundle)):
        return
    user_action(lambda: _service(ctx).complete(bundle, _owner(ctx, owner)))
    emit_json({"bundle_uuid": str(bundle), "completed": True})


@app.command("abandon")
def abandon(
    ctx: typer.Context,
    bundle: Annotated[UUID, typer.Option("--bundle")],
    owner: Annotated[str | None, typer.Option("--owner")] = None,
) -> None:
    """Release one retained bundle under its durable owner identity."""
    if _emit_bypass("abandon", bundle_uuid=str(bundle)):
        return
    user_action(lambda: _service(ctx).abandon(bundle, _owner(ctx, owner)))
    emit_json({"bundle_uuid": str(bundle), "abandoned": True})
