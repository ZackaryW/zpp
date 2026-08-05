from __future__ import annotations

import os
from pathlib import Path

import pytest

from zpp.utils.behavior_mapping import NxProvider
from zpp.utils.models import ManagedStateError
from zpp.utils.nx_provider import (
    build_nx_argv,
    discover_nx_executable,
    inspect_nx_surface,
)
from zpp.utils.processes import ProcessResult


def test_discovery_prefers_repository_local_wrapper_over_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = tmp_path / "node_modules" / ".bin" / (
        "nx.cmd" if os.name == "nt" else "nx"
    )
    local.parent.mkdir(parents=True)
    local.write_text("wrapper\n", encoding="utf-8")
    monkeypatch.setattr("zpp.utils.nx_provider.shutil.which", lambda _: "/path/nx")

    assert discover_nx_executable(tmp_path) == local.resolve()


def test_discovery_uses_path_without_downloading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("zpp.utils.nx_provider.shutil.which", lambda name: "/path/nx")

    assert discover_nx_executable(tmp_path) == Path("/path/nx")


def test_inspection_validates_project_target_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, ...]] = []

    def run(argv, *, cwd):
        calls.append(tuple(argv))
        if argv[2] == "projects":
            return ProcessResult(tuple(argv), 0, '["core", "workflow"]', "")
        project = argv[3]
        return ProcessResult(
            tuple(argv), 0, f'{{"name":"{project}","targets":{{"bdd":{{}}}}}}', ""
        )

    monkeypatch.setattr("zpp.utils.nx_provider.run_process", run)

    surface = inspect_nx_surface(Path("nx"), tmp_path)

    assert surface.projects == {
        "core": frozenset({"bdd"}),
        "workflow": frozenset({"bdd"}),
    }
    assert calls[0] == ("nx", "show", "projects", "--json")


@pytest.mark.parametrize(
    ("stdout", "returncode"),
    [("not-json", 0), ("[]", 2), ('{"project":"wrong-shape"}', 0)],
)
def test_inspection_fails_closed_for_invalid_nx_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
    returncode: int,
) -> None:
    monkeypatch.setattr(
        "zpp.utils.nx_provider.run_process",
        lambda argv, *, cwd: ProcessResult(tuple(argv), returncode, stdout, "failed"),
    )

    with pytest.raises(ManagedStateError, match="Nx workspace surface"):
        inspect_nx_surface(Path("nx"), tmp_path)


def test_build_nx_argv_uses_only_declared_projects_target_and_args() -> None:
    provider = NxProvider(target="bdd", args=("--skip-nx-cache",))

    assert build_nx_argv(Path("nx"), provider, ("core", "workflow")) == (
        "nx",
        "run-many",
        "--target",
        "bdd",
        "--projects",
        "core,workflow",
        "--skip-nx-cache",
    )
