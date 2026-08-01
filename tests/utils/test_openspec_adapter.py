from pathlib import Path

import pytest

from zpp.utils.openspec_adapter import (
    OpenSpecMember,
    create_openspec_workset,
    list_openspec_worksets,
    open_openspec_workset,
    register_private_store,
    remove_openspec_workset,
    resolve_openspec_relations,
)
from zpp.utils.processes import ProcessResult


def _result(argv: tuple[str, ...], stdout: str = "", returncode: int = 0) -> ProcessResult:
    return ProcessResult(argv, returncode, stdout, "failed" if returncode else "")


def test_openspec_workset_adapter_preserves_order_ids_and_exact_arguments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[tuple[str, ...], Path | None, dict[str, str] | None]] = []
    outputs = iter(
        (
            '{"worksets":[{"name":"组","members":[{"name":"二","path":"'
            + str(tmp_path / "二").replace("\\", "\\\\")
            + '"},{"name":"一","path":"'
            + str(tmp_path / "一").replace("\\", "\\\\")
            + '"}]}]}',
            '{"workset":{"name":"new","members":[]}}',
            "",
            "",
            "",
        )
    )

    def fake_run(argv, *, cwd=None, env=None):
        arguments = tuple(argv)
        calls.append((arguments, cwd, None if env is None else dict(env)))
        return _result(arguments, next(outputs))

    monkeypatch.setattr("zpp.utils.openspec_adapter.run_process", fake_run)
    environment = {"XDG_DATA_HOME": str(tmp_path / "private")}

    listed = list_openspec_worksets(env=environment)
    created = create_openspec_workset(
        "new",
        (OpenSpecMember("first", tmp_path / "one"),),
        env=environment,
    )
    remove_openspec_workset("new", env=environment)
    assert open_openspec_workset("组", tool="code", env=environment) == 0
    register_private_store("shared-id", tmp_path / "store", env=environment)

    assert [member.name for member in listed[0].members] == ["二", "一"]
    assert created.name == "new"
    assert calls[1][0] == (
        "openspec",
        "workset",
        "create",
        "new",
        "--member",
        f"first={tmp_path / 'one'}",
        "--json",
    )
    assert calls[2][0][-2:] == ("--yes", "--json")
    assert calls[3][0][-2:] == ("--tool", "code")
    assert calls[4][0][-4:] == ("--id", "shared-id", "--yes", "--json")
    assert all(call[2] == environment for call in calls)


def test_openspec_context_classifies_governing_and_reference_stores(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = str(tmp_path / "root").replace("\\", "\\\\")
    reference = str(tmp_path / "reference").replace("\\", "\\\\")
    payload = (
        '{"root":{"path":"'
        + root
        + '","store_id":"governance","role":"openspec_root"},'
        + '"members":[{"path":"'
        + reference
        + '","store_id":"shared","role":"reference"}]}'
    )
    monkeypatch.setattr(
        "zpp.utils.openspec_adapter.run_process",
        lambda argv, **kwargs: _result(tuple(argv), payload),
    )

    relations = resolve_openspec_relations(tmp_path)

    assert [(item.store_id, item.role) for item in relations] == [
        ("governance", "governing"),
        ("shared", "reference"),
    ]


def test_openspec_context_rejects_an_unclassified_path_bearing_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    member = str(tmp_path / "member").replace("\\", "\\\\")
    payload = (
        '{"root":{"path":"'
        + str(tmp_path).replace("\\", "\\\\")
        + '","role":"openspec_root"},"members":[{"path":"'
        + member
        + '","store_id":"unknown","role":"unexpected"}]}'
    )
    monkeypatch.setattr(
        "zpp.utils.openspec_adapter.run_process",
        lambda argv, **kwargs: _result(tuple(argv), payload),
    )

    with pytest.raises(ValueError, match="unclassified OpenSpec store relation"):
        resolve_openspec_relations(tmp_path)


def test_openspec_adapter_rejects_malformed_json_and_nonzero_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "zpp.utils.openspec_adapter.run_process",
        lambda argv, **kwargs: _result(tuple(argv), "not-json"),
    )
    with pytest.raises(ValueError, match="invalid JSON"):
        list_openspec_worksets()

    monkeypatch.setattr(
        "zpp.utils.openspec_adapter.run_process",
        lambda argv, **kwargs: _result(tuple(argv), returncode=2),
    )
    with pytest.raises(ValueError, match="failed"):
        list_openspec_worksets()
