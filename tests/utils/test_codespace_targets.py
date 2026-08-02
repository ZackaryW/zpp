import json
from pathlib import Path

import pytest

from zpp.utils.codespace_targets import (
    CodespaceTarget,
    explicit_codespace_targets,
    resolve_codespace_members,
)
from zpp.utils.git_layers import GitCheckout
from zpp.utils.openspec_adapter import OpenSpecMember, OpenSpecStoreRelation


def test_explicit_targets_accept_workspace_or_writable_paths_but_never_both(
    tmp_path: Path,
) -> None:
    project = tmp_path / "项目"
    project.mkdir()
    workspace = tmp_path / "sample.code-workspace"
    workspace.write_text(
        json.dumps({"folders": [{"path": "项目"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    assert explicit_codespace_targets(
        workspace=workspace, writable_paths=(), read_only_paths=()
    )[0].path == project.resolve()
    assert explicit_codespace_targets(
        workspace=None, writable_paths=(project,), read_only_paths=()
    )[0].path == project.resolve()
    assert explicit_codespace_targets(
        workspace=None, writable_paths=(), read_only_paths=()
    ) is None
    with pytest.raises(ValueError, match="workspace or paths"):
        explicit_codespace_targets(
            workspace=workspace,
            writable_paths=(project,),
            read_only_paths=(),
        )


def test_resolve_codespace_members_deduplicates_writable_physical_checkouts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = (tmp_path / "project").resolve()
    store = (tmp_path / "store").resolve()
    reference = (tmp_path / "reference").resolve()
    checkouts = {
        project: GitCheckout(project, project / ".git", "project-head", False),
        store: GitCheckout(store, store / ".git", "store-head", False),
        reference: GitCheckout(reference, reference / ".git", "ref-head", False),
    }

    monkeypatch.setattr(
        "zpp.utils.codespace_targets.inspect_git_checkout",
        lambda path: checkouts[path.resolve()],
    )
    monkeypatch.setattr(
        "zpp.utils.codespace_targets.resolve_openspec_relations",
        lambda _path: (
            OpenSpecStoreRelation("local", project, "governing"),
            OpenSpecStoreRelation("shared", store, "governing"),
            OpenSpecStoreRelation("reference", reference, "reference"),
        ),
    )

    resolved = resolve_codespace_members(
        (
            CodespaceTarget("project", project, "writable"),
            CodespaceTarget("duplicate", project, "writable"),
        )
    )

    assert [(item.kind, item.name) for item in resolved] == [
        ("project", "project"),
        ("store", "shared"),
    ]
    assert len({item.checkout_key for item in resolved}) == 2
