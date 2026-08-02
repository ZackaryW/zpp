from collections.abc import Collection, Iterable
from datetime import datetime
import os
from pathlib import Path
import re

from zpp.utils.models import CanonicalDirectory, SavedBinding, SavedIndex


_LAYER_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def user_zpp_root(home: Path) -> Path:
    return home / ".zpp"


def next_global_archive_name(
    when: datetime,
    existing_names: Collection[str],
) -> str:
    base = f"{when:%Y%m%d-%H%M%S}-global"
    if base not in existing_names:
        return base
    suffix = 1
    while f"{base}-{suffix}" in existing_names:
        suffix += 1
    return f"{base}-{suffix}"


def canonicalize_existing_directory(path: Path) -> CanonicalDirectory:
    resolved = path.resolve(strict=True)
    if not resolved.is_dir():
        raise NotADirectoryError(path)
    return CanonicalDirectory(
        display=path,
        resolved=resolved,
        key=os.path.normcase(os.path.normpath(str(resolved))),
    )


def path_is_within(
    path: CanonicalDirectory,
    ancestor: CanonicalDirectory,
) -> bool:
    try:
        return os.path.commonpath((path.key, ancestor.key)) == ancestor.key
    except ValueError:
        return False


def closest_saved_binding(
    target: CanonicalDirectory,
    bindings: Iterable[SavedBinding],
) -> SavedBinding | None:
    matches = [binding for binding in bindings if path_is_within(target, binding.target)]
    if not matches:
        return None
    return max(matches, key=lambda binding: len(binding.target.resolved.parts))


def validate_layer_name(name: str) -> str:
    if _LAYER_NAME.fullmatch(name) is None:
        raise ValueError(f"invalid layer name: {name!r}")
    return name


def bind_saved_target(
    index: SavedIndex,
    *,
    name: str,
    target: CanonicalDirectory,
) -> SavedIndex:
    validate_layer_name(name)
    key = str(target.resolved)
    owner = index.bindings.get(key)
    if owner is not None and owner != name:
        raise ValueError(f"saved target {key!r} is already bound to {owner!r}")
    bindings = dict(index.bindings)
    bindings[key] = name
    return SavedIndex(bindings)


def unbind_saved_name(index: SavedIndex, *, name: str) -> SavedIndex:
    validate_layer_name(name)
    return SavedIndex(
        {target: owner for target, owner in index.bindings.items() if owner != name}
    )


def ordered_saved_bindings(index: SavedIndex) -> tuple[SavedBinding, ...]:
    bindings = (
        SavedBinding(
            name=name,
            target=canonicalize_existing_directory(Path(target)),
        )
        for target, name in index.bindings.items()
    )
    return tuple(sorted(bindings, key=lambda item: item.target.key))
