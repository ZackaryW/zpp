from __future__ import annotations

from pathlib import Path

from zpp.utils.models import AuthoredLayerPaths, LayerRef, TraitCachePaths


def authored_layer_paths(root: Path) -> AuthoredLayerPaths:
    return AuthoredLayerPaths(
        root=root,
        config=root / "config.json",
        triggers=root / "trait.json",
        traits=root / "traits",
    )


def trait_cache_paths(layer: LayerRef, *, user_root: Path) -> TraitCachePaths:
    if layer.kind == "global":
        root = user_root / "cached" / "global"
    elif layer.kind in {"profile", "saved"}:
        if layer.name is None:
            raise ValueError(f"{layer.kind} layer requires a name")
        collection = "profiles" if layer.kind == "profile" else "saved"
        root = user_root / "cached" / collection / layer.name
    else:
        root = layer.root / "cached"
    return TraitCachePaths(
        root=root,
        index=root / "traits.json",
        watch=root / "traits.watch.json",
    )
