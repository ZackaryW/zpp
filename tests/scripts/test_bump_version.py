from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "bump_version.py"


def load_script():
    spec = importlib.util.spec_from_file_location("zpp_bump_version", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_project(
    root: Path,
    *,
    project_version: str = "0.9.5",
    runtime_version: str = "0.9.4",
    lock: bytes | None = b"version = 1\n",
) -> None:
    (root / "src" / "zpp").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        "[project]\n"
        'name = "zpp"\n'
        f'version = "{project_version}"  # release\n'
        "\n[tool.pytest.ini_options]\n"
        'addopts = "-q"\n',
        encoding="utf-8",
    )
    (root / "src" / "zpp" / "__init__.py").write_text(
        '"""ZPP public package."""\n\n'
        f'__version__ = "{runtime_version}"\n',
        encoding="utf-8",
    )
    if lock is not None:
        (root / "uv.lock").write_bytes(lock)


def test_bump_version_synchronizes_authored_sources_and_regenerates_lock(
    tmp_path: Path,
) -> None:
    module = load_script()
    make_project(tmp_path)

    def run_lock(root: Path) -> None:
        assert root == tmp_path
        assert 'version = "0.9.6"  # release' in (root / "pyproject.toml").read_text()
        assert '__version__ = "0.9.6"' in (
            root / "src" / "zpp" / "__init__.py"
        ).read_text()
        (root / "uv.lock").write_bytes(b"version = 1\npackage = 0.9.6\n")

    module.bump_version(tmp_path, "0.9.6", run_lock=run_lock)

    assert 'version = "0.9.6"  # release' in (tmp_path / "pyproject.toml").read_text()
    assert 'addopts = "-q"' in (tmp_path / "pyproject.toml").read_text()
    assert '__version__ = "0.9.6"' in (
        tmp_path / "src" / "zpp" / "__init__.py"
    ).read_text()
    assert (tmp_path / "uv.lock").read_bytes() == b"version = 1\npackage = 0.9.6\n"


def test_bump_version_is_idempotent(tmp_path: Path) -> None:
    module = load_script()
    make_project(tmp_path, project_version="0.9.6", runtime_version="0.9.6")
    before = {
        path: path.read_bytes()
        for path in (
            tmp_path / "pyproject.toml",
            tmp_path / "src" / "zpp" / "__init__.py",
            tmp_path / "uv.lock",
        )
    }

    module.bump_version(tmp_path, "0.9.6", run_lock=lambda _root: None)
    module.bump_version(tmp_path, "0.9.6", run_lock=lambda _root: None)

    assert {path: path.read_bytes() for path in before} == before


@pytest.mark.parametrize("target", ("1", "1.2", "v1.2.3", "1.02.3", "1.2.3-rc1"))
def test_bump_version_rejects_non_stable_semantic_versions(
    tmp_path: Path,
    target: str,
) -> None:
    module = load_script()
    make_project(tmp_path)

    with pytest.raises(module.VersionBumpError, match="X.Y.Z"):
        module.bump_version(tmp_path, target, run_lock=lambda _root: None)


@pytest.mark.parametrize(
    ("relative_path", "replacement"),
    (
        ("pyproject.toml", '[project]\nname = "zpp"\n'),
        (
            "pyproject.toml",
            '[project]\nversion = "0.9.5"\nversion = "0.9.4"\n',
        ),
        ("src/zpp/__init__.py", '"""ZPP."""\n'),
        (
            "src/zpp/__init__.py",
            '__version__ = "0.9.5"\n__version__ = "0.9.4"\n',
        ),
    ),
)
def test_bump_version_rejects_missing_or_ambiguous_declarations(
    tmp_path: Path,
    relative_path: str,
    replacement: str,
) -> None:
    module = load_script()
    make_project(tmp_path)
    (tmp_path / relative_path).write_text(replacement, encoding="utf-8")

    with pytest.raises(module.VersionBumpError, match="exactly one"):
        module.bump_version(tmp_path, "0.9.6", run_lock=lambda _root: None)


@pytest.mark.parametrize("lock_exists", (True, False))
def test_bump_version_restores_all_owned_files_when_uv_lock_fails(
    tmp_path: Path,
    lock_exists: bool,
) -> None:
    module = load_script()
    make_project(tmp_path, lock=b"original lock\n" if lock_exists else None)
    paths = (
        tmp_path / "pyproject.toml",
        tmp_path / "src" / "zpp" / "__init__.py",
        tmp_path / "uv.lock",
    )
    before = {path: path.read_bytes() if path.exists() else None for path in paths}

    def fail_lock(root: Path) -> None:
        (root / "uv.lock").write_bytes(b"partial lock\n")
        raise subprocess.CalledProcessError(1, ["uv", "lock"])

    with pytest.raises(subprocess.CalledProcessError):
        module.bump_version(tmp_path, "0.9.6", run_lock=fail_lock)

    assert {
        path: path.read_bytes() if path.exists() else None for path in paths
    } == before
