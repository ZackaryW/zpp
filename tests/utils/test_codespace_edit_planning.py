import json
from pathlib import Path

import pytest

from zpp.utils.codespace_edits import normalize_codespace_edit
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember
from zpp.utils.codespace_planning import ResolvedMember, plan_codespace_edit
from zpp.utils.codespace_targets import (
    CodespaceTarget,
    explicit_codespace_targets,
    resolve_codespace_members,
)
from zpp.utils.git_layers import GitCheckout
from zpp.utils.openspec_adapter import OpenSpecStoreRelation


def _checkout(path: Path, head: str, *, dirty: bool = False) -> GitCheckout:
    root = path.resolve()
    return GitCheckout(root, root / ".git", head, dirty)


def _member(
    path: Path,
    name: str,
    key: str,
    *,
    access: str = "writable",
    generated: bool = False,
) -> CodespaceMember:
    return CodespaceMember(
        name=name,
        original_path=path,
        effective_path=(path.parent / f"{path.name}-old" if generated else path),
        checkout_key=(f"effective-{key}" if generated else key),
        source_checkout_key=key,
        commit=f"commit-{key}",
        kind="project",
        access=access,
        generated_worktree=generated,
        branch=(f"zpp/old/{key}" if generated else None),
    )


def _resolved(
    path: Path,
    name: str,
    key: str,
    *,
    access: str,
    dirty: bool = False,
) -> ResolvedMember:
    return ResolvedMember(
        name=name,
        checkout=_checkout(path, f"head-{key}", dirty=dirty),
        checkout_key=key,
        kind="project",
        access=access,
    )


def test_explicit_mixed_targets_expand_only_writable_projects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = (tmp_path / "project").resolve()
    store = (tmp_path / "store").resolve()
    reference = (tmp_path / "reference").resolve()
    project.mkdir()
    store.mkdir()
    reference.mkdir()
    workspace = tmp_path / "view.code-workspace"
    workspace.write_text(
        json.dumps({"folders": [{"path": "project"}]}),
        encoding="utf-8",
    )
    checkouts = {
        project: _checkout(project, "project-head"),
        store: _checkout(store, "store-head"),
        reference: _checkout(reference, "reference-head"),
    }
    relation_calls: list[Path] = []
    monkeypatch.setattr(
        "zpp.utils.codespace_targets.inspect_git_checkout",
        lambda path: checkouts[path.resolve()],
    )
    monkeypatch.setattr(
        "zpp.utils.codespace_targets.resolve_openspec_relations",
        lambda path: relation_calls.append(path)
        or (OpenSpecStoreRelation("store", store, "governing"),),
    )

    targets = explicit_codespace_targets(
        workspace=workspace,
        writable_paths=(),
        read_only_paths=(reference,),
    )
    assert targets is not None
    resolved = resolve_codespace_members(targets)

    assert [(member.name, member.access) for member in resolved] == [
        ("project", "writable"),
        ("store", "writable"),
        ("reference", "read_only"),
    ]
    assert relation_calls == [project]


def test_edit_normalization_rejects_two_operations_for_one_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    monkeypatch.setattr(
        "zpp.utils.codespace_edits.inspect_git_checkout",
        lambda path: _checkout(path, "head"),
    )

    with pytest.raises(ValueError, match="contradictory"):
        normalize_codespace_edit(
            add=(project,),
            add_read_only=(),
            remove=(project / ".",),
            promote=(),
            demote=(),
        )


def test_edit_plan_replaces_identity_and_partitions_generated_debt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    keep = _member(tmp_path / "keep", "keep", "keep")
    remove = _member(tmp_path / "remove", "remove", "remove", access="read_only")
    demote = _member(tmp_path / "demote", "demote", "demote", generated=True)
    promote = _member(tmp_path / "promote", "promote", "promote", access="read_only")
    current = CodespaceClaim(
        instance_id="old",
        snapshot_key="old-snapshot",
        members=(keep, remove, demote, promote),
    )
    other = CodespaceClaim(
        instance_id="other",
        snapshot_key="other-snapshot",
        members=(_member(tmp_path / "other", "other", "promote"),),
    )
    checkouts = {
        path.resolve(): _checkout(path, f"head-{path.name}")
        for path in (
            tmp_path / "new",
            tmp_path / "reference",
            remove.original_path,
            demote.original_path,
            promote.original_path,
        )
    }
    monkeypatch.setattr(
        "zpp.utils.codespace_edits.inspect_git_checkout",
        lambda path: checkouts[path.resolve()],
    )
    monkeypatch.setattr(
        "zpp.utils.codespace_edits.checkout_claim_key",
        lambda checkout: checkout.root.name,
    )
    operations = normalize_codespace_edit(
        add=(tmp_path / "new",),
        add_read_only=(tmp_path / "reference",),
        remove=(remove.original_path,),
        promote=(promote.original_path,),
        demote=(demote.original_path,),
    )
    resolved = (
        _resolved(tmp_path / "new", "new", "new", access="writable", dirty=True),
        _resolved(tmp_path / "reference", "reference", "reference", access="read_only"),
        _resolved(promote.original_path, "promote", "promote", access="writable"),
    )

    plan = plan_codespace_edit(
        current,
        operations,
        resolved,
        CodespaceIndex(claims={"old": current, "other": other}),
        successor_id="successor",
    )

    assert not plan.no_op
    assert plan.successor is not None and plan.successor.instance_id == "successor"
    assert plan.successor.snapshot_key != current.snapshot_key
    assert {member.name: member.access for member in plan.successor.members} == {
        "keep": "writable",
        "demote": "read_only",
        "promote": "writable",
        "new": "writable",
        "reference": "read_only",
    }
    promoted = next(member for member in plan.successor.members if member.name == "promote")
    assert promoted.generated_worktree and promoted.checkout_key != "promote"
    assert plan.conflicting_checkout_keys == ("promote",)
    assert plan.dirty_member_names == ("new",)
    assert plan.released is not None
    assert [debt.checkout_key for debt in plan.released.debts] == ["effective-demote"]


def test_edit_plan_reports_a_structurally_unchanged_request_as_no_op(
    tmp_path: Path,
) -> None:
    current = CodespaceClaim(
        instance_id="current",
        snapshot_key="snapshot",
        members=(_member(tmp_path / "keep", "keep", "keep"),),
    )
    operations = normalize_codespace_edit(
        add=(), add_read_only=(), remove=(), promote=(), demote=()
    )

    plan = plan_codespace_edit(
        current,
        operations,
        (),
        CodespaceIndex(claims={"current": current}),
        successor_id="unused",
    )

    assert plan.no_op and plan.successor is None and plan.released is None
