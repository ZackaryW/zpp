from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ZppHome:
    path: Path

    @property
    def state_root(self) -> Path:
        return self.path / "bundler"

    @property
    def identity_path(self) -> Path:
        return self.path / "identity.json"

    @property
    def workflow_reminder_root(self) -> Path:
        return self.path / "workflow-reminders"


class WorkflowIdentityRepository:
    """Strict durable owner identity scoped to one selected ZPP home."""

    def __init__(self, home: ZppHome) -> None:
        self._home = home

    @staticmethod
    def _decode(text: str, *, source: Path) -> str:
        try:
            document = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"{source}: invalid workflow identity JSON") from error
        if not isinstance(document, dict):
            raise ValueError(f"{source}: workflow identity must be an object")
        if set(document) != {"owner_id", "version"}:
            raise ValueError(f"{source}: workflow identity has invalid fields")
        if document["version"] != 1 or isinstance(document["version"], bool):
            raise ValueError(f"{source}: workflow identity version must be integer 1")
        owner_id = document["owner_id"]
        if not isinstance(owner_id, str) or not owner_id.startswith("zpp:"):
            raise ValueError(f"{source}: workflow identity owner_id is invalid")
        try:
            identity = UUID(owner_id.removeprefix("zpp:"))
        except ValueError as error:
            raise ValueError(
                f"{source}: workflow identity owner_id is invalid"
            ) from error
        if identity.version != 4 or str(identity) != owner_id.removeprefix("zpp:"):
            raise ValueError(f"{source}: workflow identity owner_id is invalid")
        return owner_id

    def resolve(self) -> str:
        path = self._home.identity_path
        try:
            return self._decode(path.read_text(encoding="utf-8"), source=path)
        except FileNotFoundError:
            pass
        self._home.path.mkdir(parents=True, exist_ok=True)
        owner_id = f"zpp:{uuid4()}"
        payload = (
            json.dumps(
                {"owner_id": owner_id, "version": 1},
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
        except FileExistsError:
            return self._decode(path.read_text(encoding="utf-8"), source=path)
        return owner_id


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
        raise ValueError("ZPP Bundler state cannot be a symlink")
    if state_root.exists() and not state_root.is_dir():
        raise ValueError("ZPP Bundler state must be a directory")


@dataclass(slots=True)
class PreparedBundlerState:
    home: ZppHome
    staging_root: Path

    @property
    def staged_state(self) -> Path:
        return self.staging_root / "bundler"

    @classmethod
    def prepare(cls, home: ZppHome) -> PreparedBundlerState:
        validate_reset_boundary(home)
        home.path.mkdir(parents=True, exist_ok=True)
        staging_root = Path(tempfile.mkdtemp(prefix=".zpp-reset-", dir=home.path))
        prepared = cls(home, staging_root)
        try:
            prepared.staged_state.mkdir()
            from openspec_bundler import LeaseStateRepository

            LeaseStateRepository(prepared.staged_state).read()
        except BaseException:
            prepared.discard()
            raise
        return prepared

    def replace(self) -> None:
        validate_reset_boundary(self.home)
        if self.staging_root.is_symlink() or not self.staging_root.is_dir():
            raise ValueError("prepared Bundler staging root is unavailable")
        if self.staged_state.is_symlink() or not self.staged_state.is_dir():
            raise ValueError("prepared Bundler state is unavailable")

        current = self.home.state_root
        backup = self.staging_root / "previous-bundler"
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
