from __future__ import annotations

import json
from contextlib import suppress
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from zpp.utils.agent_hooks import (
    claude_pre_tool_use_hook,
    claude_session_start_hook,
    codex_pre_tool_use_hook,
    codex_session_start_hook,
    reconcile_claude_settings,
    reconcile_codex_hooks,
)
from zpp.utils.json_io import atomic_write_json
from zpp.utils.models import (
    CreationEntry,
    CreationPlan,
    ManagedStateError,
    PackagedPiExtension,
)
from zpp.utils.state_mutation import apply_creation_plan


ManagedArtifactState = Literal["missing", "identical", "conflict"]


def inspect_pi_extension(
    destination: Path,
    expected: PackagedPiExtension,
) -> ManagedArtifactState:
    if not destination.exists() and not destination.is_symlink():
        return "missing"
    if destination.is_symlink() or not destination.is_file():
        return "conflict"
    try:
        source = destination.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "conflict"
    return "identical" if source == expected.source else "conflict"


def install_pi_extension(destination: Path, expected: PackagedPiExtension) -> None:
    state = inspect_pi_extension(destination, expected)
    if state == "identical":
        return
    if state == "conflict":
        raise ManagedStateError(f"unmanaged Pi extension exists at {destination}")

    entries = _missing_parent_entries(destination.parent)
    entries.append(CreationEntry(destination, "text", expected.source))
    apply_creation_plan(CreationPlan(tuple(entries)))


def load_packaged_pi_extension() -> PackagedPiExtension:
    source = (
        files("zpp.artifacts")
        .joinpath("pi")
        .joinpath("index.ts")
        .read_text(encoding="utf-8")
    )
    return PackagedPiExtension(source)


def preflight_pi(home: Path, artifact: PackagedPiExtension) -> None:
    destination = home / ".pi" / "agent" / "extensions" / "zpp" / "index.ts"
    state = inspect_pi_extension(destination, artifact)
    if state == "conflict":
        raise ManagedStateError(f"unmanaged Pi extension exists at {destination}")
    if state == "missing":
        _missing_parent_entries(destination.parent)


def preflight_codex(home: Path) -> None:
    destination = home / ".codex" / "hooks.json"
    _prepare_codex(destination)


def preflight_claude_code(home: Path) -> None:
    destination = home / ".claude" / "settings.json"
    _prepare_claude_code(destination)


def bootstrap_pi(
    home: Path,
    artifact: PackagedPiExtension,
) -> None:
    destination = home / ".pi" / "agent" / "extensions" / "zpp" / "index.ts"
    preflight_pi(home, artifact)
    install_pi_extension(destination, artifact)


def bootstrap_codex(home: Path) -> None:
    destination = home / ".codex" / "hooks.json"
    current, reconciled = _prepare_codex(destination)
    _write_json_if_changed(destination, current, reconciled)


def bootstrap_claude_code(home: Path) -> None:
    destination = home / ".claude" / "settings.json"
    current, reconciled = _prepare_claude_code(destination)
    _write_json_if_changed(destination, current, reconciled)


def _prepare_codex(destination: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    current = _read_json_object(destination)
    reconciled = reconcile_codex_hooks(current, codex_session_start_hook())
    reconciled = reconcile_codex_hooks(reconciled, codex_pre_tool_use_hook())
    if current != reconciled:
        _missing_parent_entries(destination.parent)
    return current, reconciled


def _prepare_claude_code(
    destination: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    current = _read_json_object(destination)
    reconciled = reconcile_claude_settings(current, claude_session_start_hook())
    reconciled = reconcile_claude_settings(reconciled, claude_pre_tool_use_hook())
    if current != reconciled:
        _missing_parent_entries(destination.parent)
    return current, reconciled


def _read_json_object(destination: Path) -> dict[str, Any] | None:
    if not destination.exists() and not destination.is_symlink():
        return None
    if destination.is_symlink() or not destination.is_file():
        raise ManagedStateError(f"managed JSON destination is not a regular file: {destination}")
    try:
        value = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManagedStateError(f"managed JSON destination is unreadable: {destination}") from error
    if not isinstance(value, dict):
        raise ManagedStateError(f"managed JSON destination is not an object: {destination}")
    return value


def _write_json_if_changed(
    destination: Path,
    current: dict[str, Any] | None,
    reconciled: dict[str, Any],
) -> None:
    if current == reconciled:
        return

    entries = _missing_parent_entries(destination.parent)
    if entries:
        apply_creation_plan(CreationPlan(tuple(entries)))
    try:
        atomic_write_json(destination, reconciled)
    except BaseException:
        for entry in reversed(entries):
            with suppress(OSError):
                entry.path.rmdir()
        raise


def _missing_parent_entries(parent: Path) -> list[CreationEntry]:
    missing: list[Path] = []
    cursor = parent
    while not cursor.exists() and not cursor.is_symlink():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise ManagedStateError(f"managed destination parent is not a directory: {cursor}")
    return [CreationEntry(path, "directory") for path in reversed(missing)]
