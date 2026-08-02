"""Transactional authored-layer replacement utilities."""

from collections.abc import Iterable
from pathlib import Path

from zpp.utils.authored_layers import (
    authored_layer_creation_plan,
    collect_authored_layer,
)
from zpp.utils.models import AuthoredLayerPaths, AuthoredLayerSnapshot
from zpp.utils.removals import stage_removals
from zpp.utils.state_mutation import apply_creation_plan


def archive_and_replace_authored_layer(
    current: AuthoredLayerPaths,
    replacement: AuthoredLayerSnapshot,
    archive: Path,
    cache_roots: Iterable[Path],
) -> None:
    """Archive the current layer, install its replacement, and clear caches."""

    collect_authored_layer(current.root)
    if archive.exists() or archive.is_symlink():
        raise FileExistsError(archive)
    if archive.parent.is_symlink() or not archive.parent.is_dir():
        raise NotADirectoryError(archive.parent)

    cache_transaction = stage_removals(cache_roots)
    archived = False
    try:
        current.root.replace(archive)
        archived = True
        apply_creation_plan(authored_layer_creation_plan(replacement, current.root))
    except BaseException:
        partial_replacement = None
        if archived:
            partial_replacement = stage_removals((current.root,))
            archive.replace(current.root)
        cache_transaction.restore()
        if partial_replacement is not None:
            partial_replacement.commit()
        raise
    cache_transaction.commit()
