from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ZppHome:
    path: Path

    @property
    def state_root(self) -> Path:
        return self.path / "openlease"


def selected_zpp_home(
    path: Path | None,
    *,
    user_home: Path | None = None,
) -> ZppHome:
    selected = (user_home or Path.home()) / ".zpp" if path is None else path
    expanded = selected.expanduser()
    normalized = Path(os.path.abspath(os.fspath(expanded)))
    return ZppHome(normalized)


def validate_reset_boundary(home: ZppHome) -> None:
    root = home.path
    if root == Path(root.anchor):
        raise ValueError("ZPP home cannot be a filesystem root")
    if root.is_symlink():
        raise ValueError("ZPP home cannot be a symlink")
    if root.exists() and not root.is_dir():
        raise ValueError("ZPP home must be a directory")

    state_root = home.state_root
    if state_root.is_symlink():
        raise ValueError("ZPP openlease state cannot be a symlink")
    if state_root.exists() and not state_root.is_dir():
        raise ValueError("ZPP openlease state must be a directory")


@dataclass(slots=True)
class PreparedOpenLeaseState:
    home: ZppHome
    staging_root: Path

    @property
    def staged_state(self) -> Path:
        return self.staging_root / "openlease"

    @classmethod
    def prepare(cls, home: ZppHome) -> PreparedOpenLeaseState:
        validate_reset_boundary(home)
        home.path.mkdir(parents=True, exist_ok=True)
        staging_root = Path(tempfile.mkdtemp(prefix=".zpp-reset-", dir=home.path))
        prepared = cls(home, staging_root)
        try:
            prepared.staged_state.mkdir()
            from zpp.utils.openlease import create_zpp_openlease

            create_zpp_openlease(prepared.staged_state).snapshot()
        except BaseException:
            prepared.discard()
            raise
        return prepared

    def replace(self) -> None:
        validate_reset_boundary(self.home)
        if self.staging_root.is_symlink() or not self.staging_root.is_dir():
            raise ValueError("prepared OpenLease staging root is unavailable")
        if self.staged_state.is_symlink() or not self.staged_state.is_dir():
            raise ValueError("prepared OpenLease state is unavailable")

        current = self.home.state_root
        backup = self.staging_root / "previous-openlease"
        had_current = current.exists()
        if had_current:
            current.rename(backup)
        try:
            self.staged_state.rename(current)
        except BaseException:
            if had_current:
                backup.rename(current)
            raise

        if backup.exists():
            shutil.rmtree(backup)
        self.staging_root.rmdir()

    def discard(self) -> None:
        if self.staging_root.exists() and not self.staging_root.is_symlink():
            shutil.rmtree(self.staging_root)
