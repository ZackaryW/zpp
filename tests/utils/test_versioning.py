from pathlib import Path

import pytest

from zpp.utils.versioning import synchronize_version


def _write_release_files(
    root: Path,
    *,
    project: str = "1.0.0",
    runtime: str = "0.9.0",
    lock: str | None = "1.0.0",
) -> None:
    (root / "src/zpp").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "fixture"\nversion = "{project}"\n\n[tool.fixture]\nkeep = true\n',
        encoding="utf-8",
    )
    (root / "src/zpp/__init__.py").write_text(
        f'"""fixture"""\n\n__version__ = "{runtime}"\n\nKEEP = "π"\n',
        encoding="utf-8",
    )
    if lock is not None:
        (root / "uv.lock").write_text(
            f'[[package]]\nname = "fixture"\nversion = "{lock}"\n',
            encoding="utf-8",
        )


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_synchronize_version_updates_both_sources_and_is_idempotent(
    tmp_path: Path,
) -> None:
    _write_release_files(tmp_path)
    calls: list[Path] = []

    def refresh_lock(root: Path) -> None:
        calls.append(root)
        (root / "uv.lock").write_text(
            '[[package]]\nname = "fixture"\nversion = "1.2.3"\n',
            encoding="utf-8",
        )

    first = synchronize_version(tmp_path, "1.2.3", run_lock=refresh_lock)
    after_first = _snapshot(tmp_path)
    second = synchronize_version(tmp_path, "1.2.3", run_lock=refresh_lock)

    assert first.project_version == "1.0.0"
    assert first.runtime_version == "0.9.0"
    assert first.target_version == "1.2.3"
    assert first.changed is True
    assert second.changed is False
    assert calls == [tmp_path, tmp_path]
    assert _snapshot(tmp_path) == after_first
    assert 'version = "1.2.3"' in (tmp_path / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert '__version__ = "1.2.3"' in (
        tmp_path / "src/zpp/__init__.py"
    ).read_text(encoding="utf-8")
    assert 'KEEP = "π"' in (tmp_path / "src/zpp/__init__.py").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize("target", ("1.2", "v1.2.3", "1.2.3rc1", "next"))
def test_synchronize_version_rejects_nonstable_targets_without_mutation(
    tmp_path: Path,
    target: str,
) -> None:
    _write_release_files(tmp_path)
    before = _snapshot(tmp_path)

    with pytest.raises(ValueError, match="X.Y.Z"):
        synchronize_version(
            tmp_path,
            target,
            run_lock=lambda _: pytest.fail("lock refresh must not run"),
        )

    assert _snapshot(tmp_path) == before


def test_synchronize_version_rejects_duplicate_declarations_before_writing(
    tmp_path: Path,
) -> None:
    _write_release_files(tmp_path)
    initializer = tmp_path / "src/zpp/__init__.py"
    initializer.write_text(
        initializer.read_text(encoding="utf-8") + '__version__ = "2.0.0"\n',
        encoding="utf-8",
    )
    before = _snapshot(tmp_path)

    with pytest.raises(ValueError, match="exactly one __version__"):
        synchronize_version(
            tmp_path,
            "1.2.3",
            run_lock=lambda _: pytest.fail("lock refresh must not run"),
        )

    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("existing_lock", (True, False))
def test_synchronize_version_restores_every_file_after_lock_failure(
    tmp_path: Path,
    existing_lock: bool,
) -> None:
    _write_release_files(tmp_path, lock="1.0.0" if existing_lock else None)
    before = _snapshot(tmp_path)

    def fail_after_lock_write(root: Path) -> None:
        (root / "uv.lock").write_text("partial lock\n", encoding="utf-8")
        raise RuntimeError("lock failed")

    with pytest.raises(RuntimeError, match="lock failed"):
        synchronize_version(tmp_path, "1.2.3", run_lock=fail_after_lock_write)

    assert _snapshot(tmp_path) == before
    assert (tmp_path / "uv.lock").exists() is existing_lock
