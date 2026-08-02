from pathlib import Path

from zpp.utils.layouts import authored_layer_paths, trait_cache_paths
from zpp.utils.models import LayerRef


def test_authored_and_cache_layouts_remain_independent(tmp_path: Path) -> None:
    user_root = tmp_path / ".zpp"
    global_layer = LayerRef(kind="global", root=user_root / "global")
    profile_layer = LayerRef(
        kind="profile",
        name="work",
        root=user_root / "profiles" / "work",
    )
    saved_layer = LayerRef(
        kind="saved",
        name="shared",
        root=user_root / "saved" / "shared",
    )
    local_layer = LayerRef(kind="local", root=tmp_path / "project" / ".zpp")

    authored = authored_layer_paths(profile_layer.root)

    assert authored.config == profile_layer.root / "config.json"
    assert authored.triggers == profile_layer.root / "trait.json"
    assert authored.traits == profile_layer.root / "traits"
    assert trait_cache_paths(global_layer, user_root=user_root).root == user_root / "cached" / "global"
    assert trait_cache_paths(profile_layer, user_root=user_root).root == user_root / "cached" / "profiles" / "work"
    assert trait_cache_paths(saved_layer, user_root=user_root).root == user_root / "cached" / "saved" / "shared"
    assert trait_cache_paths(local_layer, user_root=user_root).root == local_layer.root / "cached"
