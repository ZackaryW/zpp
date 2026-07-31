from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from zpp.core.errors import ZppDomainError, validation_diagnostic
from zpp.utils.authored_layers import (
    authored_layer_creation_plan,
    collect_authored_layer,
)
from zpp.utils.control_documents import validate_saved_index
from zpp.utils.git_layers import git_worktree_root
from zpp.utils.json_io import atomic_write_json
from zpp.utils.layer_inspection import inspect_authored_layer
from zpp.utils.layer_transactions import archive_and_replace_authored_layer
from zpp.utils.layouts import authored_layer_paths, trait_cache_paths
from zpp.utils.models import (
    AuthoredLayerPaths,
    CreationEntry,
    CreationPlan,
    LayerRef,
    ManagedStateError,
    SavedIndex,
    ZppValidationError,
)
from zpp.utils.packaged_profiles import load_packaged_default_profile
from zpp.utils.paths import (
    bind_saved_target,
    canonicalize_existing_directory,
    next_global_archive_name,
    ordered_saved_bindings,
    unbind_saved_name,
    user_zpp_root,
    validate_layer_name,
)
from zpp.utils.removals import stage_removals
from zpp.utils.state_mutation import apply_creation_plan


NEUTRAL_CONFIG = '{\n  "trait_overwrites": false,\n  "traitsConfig": {}\n}\n'
NEUTRAL_TRIGGERS = "[]\n"
EMPTY_SAVED_INDEX = "{}\n"


def initialize_user_state(home: Path) -> Path:
    root = user_zpp_root(home)
    entries = _user_state_creation_entries(root)
    if entries:
        apply_creation_plan(CreationPlan(tuple(entries)))
    return root


def require_initialized_user_state(home: Path) -> Path:
    root = user_zpp_root(home)
    entries = _user_state_creation_entries(root)
    if entries:
        raise ZppDomainError(f"ZPP user state is incomplete: {entries[0].path}")
    return root


def create_profile(home: Path, name: str) -> None:
    validate_layer_name(name)
    root = require_initialized_user_state(home)
    entries = _layer_creation_entries(root / "profiles" / name)
    if entries:
        apply_creation_plan(CreationPlan(tuple(entries)))


def list_profiles(home: Path) -> tuple[str, ...]:
    root = require_initialized_user_state(home)
    return tuple(sorted(path.name for path in (root / "profiles").iterdir() if path.is_dir()))


def remove_profile(home: Path, name: str) -> None:
    validate_layer_name(name)
    root = require_initialized_user_state(home)
    if name == "default":
        raise ZppDomainError("the persistent default profile cannot be removed")
    layer = root / "profiles" / name
    cache = trait_cache_paths(
        LayerRef(kind="profile", root=layer, name=name),
        user_root=root,
    ).root
    if not layer.exists() and not layer.is_symlink():
        raise ZppDomainError(f"profile does not exist: {name}")
    staged = stage_removals((layer, cache))
    staged.commit()


def copy_profile(home: Path, source_name: str, destination_name: str) -> None:
    validate_layer_name(source_name)
    validate_layer_name(destination_name)
    root = require_initialized_user_state(home)
    source = root / "profiles" / source_name
    destination = root / "profiles" / destination_name
    if not source.exists() and not source.is_symlink():
        raise ZppDomainError(f"source profile does not exist: {source_name}")
    if destination.exists() or destination.is_symlink():
        raise ZppDomainError(f"destination profile already exists: {destination_name}")
    snapshot = collect_authored_layer(source)
    apply_creation_plan(authored_layer_creation_plan(snapshot, destination))


def activate_global_profile(
    home: Path,
    name: str,
    *,
    when: datetime | None = None,
) -> str:
    validate_layer_name(name)
    root = require_initialized_user_state(home)
    source = root / "profiles" / name
    if not source.exists() and not source.is_symlink():
        raise ZppDomainError(f"source profile does not exist: {name}")
    replacement = collect_authored_layer(source)
    profile_names = {
        path.name
        for path in (root / "profiles").iterdir()
        if path.exists() or path.is_symlink()
    }
    archive_name = next_global_archive_name(when or datetime.now(), profile_names)
    global_layer = authored_layer_paths(root / "global")
    global_cache = trait_cache_paths(
        LayerRef(kind="global", root=global_layer.root),
        user_root=root,
    ).root
    archive_and_replace_authored_layer(
        global_layer,
        replacement,
        root / "profiles" / archive_name,
        (global_cache,),
    )
    return archive_name


def create_saved(home: Path, name: str, target_path: Path) -> None:
    validate_layer_name(name)
    target = canonicalize_existing_directory(target_path)
    root = require_initialized_user_state(home)
    index_path = root / "saved" / "_bindings.json"
    original = _read_saved_index(index_path)
    updated = bind_saved_target(original, name=name, target=target)
    layer_root = root / "saved" / name
    entries = _layer_creation_entries(layer_root)

    if entries:
        apply_creation_plan(CreationPlan(tuple(entries)))
    try:
        if updated != original:
            atomic_write_json(index_path, updated.bindings)
    except BaseException:
        created_roots = _created_entry_roots(entries)
        if created_roots:
            stage_removals(created_roots).commit()
        raise


def list_saved(home: Path) -> tuple[tuple[str, Path], ...]:
    root = require_initialized_user_state(home)
    index = _read_saved_index(root / "saved" / "_bindings.json")
    return tuple((binding.name, binding.target.resolved) for binding in ordered_saved_bindings(index))


def remove_saved(home: Path, name: str) -> None:
    validate_layer_name(name)
    root = require_initialized_user_state(home)
    index_path = root / "saved" / "_bindings.json"
    original = _read_saved_index(index_path)
    updated = unbind_saved_name(original, name=name)
    layer = root / "saved" / name
    cache = trait_cache_paths(
        LayerRef(kind="saved", root=layer, name=name),
        user_root=root,
    ).root
    if updated == original and not layer.exists() and not layer.is_symlink():
        raise ZppDomainError(f"saved layer does not exist: {name}")

    staged = stage_removals((layer, cache))
    try:
        if updated != original:
            atomic_write_json(index_path, updated.bindings)
    except BaseException:
        staged.restore()
        raise
    staged.commit()


def initialize_local_layer(target_path: Path) -> Path:
    target = canonicalize_existing_directory(target_path)
    worktree_path = git_worktree_root(target.resolved)
    if worktree_path is None:
        raise ZppDomainError(f"target is not inside a Git worktree: {target_path}")
    worktree = canonicalize_existing_directory(worktree_path)
    try:
        target.resolved.relative_to(worktree.resolved)
    except ValueError as error:
        raise ZppDomainError(f"target is outside its Git worktree: {target_path}") from error

    root = target.resolved / ".zpp"
    entries = _layer_creation_entries(root)
    if entries:
        apply_creation_plan(CreationPlan(tuple(entries)))
    return root


def read_saved_index(home: Path) -> SavedIndex:
    root = require_initialized_user_state(home)
    return _read_saved_index(root / "saved" / "_bindings.json")


def _user_state_creation_entries(root: Path) -> list[CreationEntry]:
    entries: list[CreationEntry] = []
    if not root.exists() and not root.is_symlink():
        entries.append(CreationEntry(root, "directory"))
    elif root.is_symlink() or not root.is_dir():
        raise ManagedStateError(f"ZPP user root is not a directory: {root}")

    for directory in (root / "profiles", root / "saved", root / "cached"):
        if not directory.exists() and not directory.is_symlink():
            entries.append(CreationEntry(directory, "directory"))
        elif directory.is_symlink() or not directory.is_dir():
            raise ManagedStateError(f"managed path is not a directory: {directory}")

    index = root / "saved" / "_bindings.json"
    if not index.exists() and not index.is_symlink():
        entries.append(CreationEntry(index, "text", EMPTY_SAVED_INDEX))
    elif index.is_symlink() or not index.is_file():
        raise ManagedStateError(f"saved binding index is not a regular file: {index}")
    else:
        _read_saved_index(index)

    entries.extend(_layer_creation_entries(root / "global"))
    default_profile = root / "profiles" / "default"
    if not default_profile.exists() and not default_profile.is_symlink():
        entries.extend(
            authored_layer_creation_plan(
                load_packaged_default_profile(),
                default_profile,
            ).entries
        )
    else:
        try:
            collect_authored_layer(default_profile)
        except (OSError, UnicodeError, ValueError) as error:
            raise ManagedStateError(
                f"invalid persistent default profile at {default_profile}: {error}"
            ) from error
    return entries


def _layer_creation_entries(root: Path) -> list[CreationEntry]:
    paths = authored_layer_paths(root)
    inspection = inspect_authored_layer(paths)
    if inspection.state == "invalid":
        details = "; ".join(
            f"{issue.source or root}: {issue.message}" for issue in inspection.issues
        )
        raise ManagedStateError(details)
    if inspection.state == "complete":
        return []
    if inspection.state == "absent":
        return [
            CreationEntry(root, "directory"),
            CreationEntry(paths.config, "text", NEUTRAL_CONFIG),
            CreationEntry(paths.triggers, "text", NEUTRAL_TRIGGERS),
            CreationEntry(paths.traits, "directory"),
        ]

    entries: list[CreationEntry] = []
    for missing in inspection.missing:
        if missing == paths.config:
            entries.append(CreationEntry(missing, "text", NEUTRAL_CONFIG))
        elif missing == paths.triggers:
            entries.append(CreationEntry(missing, "text", NEUTRAL_TRIGGERS))
        elif missing == paths.traits:
            entries.append(CreationEntry(missing, "directory"))
        else:
            raise ManagedStateError(f"unsupported missing managed path: {missing}")
    return entries


def _read_saved_index(path: Path) -> SavedIndex:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return validate_saved_index(value)
    except ZppValidationError as error:
        raise ManagedStateError(f"{path}: {validation_diagnostic(error)}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManagedStateError(f"{path}: {error}") from error


def _created_entry_roots(entries: list[CreationEntry]) -> tuple[Path, ...]:
    paths = [entry.path for entry in entries]
    return tuple(
        path
        for path in paths
        if not any(path != other and path.is_relative_to(other) for other in paths)
    )
