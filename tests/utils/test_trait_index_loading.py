from pathlib import Path

from zpp.utils.layouts import authored_layer_paths
from zpp.utils.models import LayerRef
from zpp.utils.layouts import trait_cache_paths
from zpp.utils.trait_index_loading import load_trait_index


def test_trait_index_loading_compiles_then_reuses_a_certified_cache(
    tmp_path: Path,
    monkeypatch,
) -> None:
    user_root = tmp_path / ".zpp"
    layer = LayerRef(kind="global", root=user_root / "global")
    authored = authored_layer_paths(layer.root)
    authored.traits.mkdir(parents=True)
    (authored.traits / "alpha.md").write_text(
        "---\nname: alpha\ndescription: Alpha\n---\nBody\n",
        encoding="utf-8",
    )
    cache = trait_cache_paths(layer, user_root=user_root)

    compiled = load_trait_index(authored, cache)
    monkeypatch.setattr(
        "zpp.utils.trait_index_loading.compile_trait_index",
        lambda *_: (_ for _ in ()).throw(AssertionError("cache should be reused")),
    )
    reused = load_trait_index(authored, cache)

    assert compiled == reused
    assert cache.index.is_file() and cache.watch.is_file()
