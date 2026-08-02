import json
from pathlib import Path

import pytest

from zpp.utils.layouts import authored_layer_paths, trait_cache_paths
from zpp.utils.models import LayerRef, ZppValidationError
from zpp.utils.plugin_discovery import ActivePlugin
from zpp.utils.plugin_trait_sources import (
    inspect_plugin_trait_source,
    merge_plugin_trait_indexes,
)
from zpp.utils.trait_cache import write_trait_cache_watchfile
from zpp.utils.trait_compiler import compile_trait_index
from zpp.utils.trait_composition import select_effective_documents
from zpp.utils.trait_documents import render_trait_document
from zpp.utils.trait_index_loading import load_trait_index


def _source(root: Path, identity: str, document: bytes):
    traits = root / "traits"
    traits.mkdir(parents=True)
    (root / "trait.json").write_text("[]\n", encoding="utf-8")
    (traits / "shared.md").write_bytes(document)
    source = inspect_plugin_trait_source(
        ActivePlugin("codex", identity, "1", root.resolve())
    )
    assert source is not None
    return source, compile_trait_index((traits / "shared.md",))


def test_trait_index_records_exact_authored_digest_without_rendering_it(
    tmp_path: Path,
) -> None:
    path = tmp_path / "shared.md"
    path.write_bytes(
        b"---\nname: shared\ndescription: Shared\n---\n\nBody.\n"
    )

    index = compile_trait_index((path,))
    record = index["traits"]["shared"]
    document = select_effective_documents(("shared",), (index,))[0]

    assert index["schema_version"] == 2
    assert len(record["source_sha256"]) == 64
    assert "source_sha256" not in render_trait_document(document)


def test_identical_external_definitions_deduplicate_in_identity_order(
    tmp_path: Path,
) -> None:
    document = b"---\nname: shared\ndescription: Shared\n---\n\nBody.\n"
    zeta_source, zeta_index = _source(tmp_path / "zeta", "zeta@market", document)
    alpha_source, alpha_index = _source(tmp_path / "alpha", "alpha@market", document)

    merged = merge_plugin_trait_indexes(
        (zeta_source, alpha_source),
        (zeta_index, alpha_index),
    )

    assert tuple(merged["traits"]) == ("shared",)
    assert merged["traits"]["shared"] == alpha_index["traits"]["shared"]


def test_byte_different_external_definitions_report_every_conflicting_source(
    tmp_path: Path,
) -> None:
    first_source, first_index = _source(
        tmp_path / "first",
        "first@market",
        b"---\nname: shared\ndescription: Shared\n---\n\nBody.\n",
    )
    second_source, second_index = _source(
        tmp_path / "second",
        "second@market",
        b"---\nname: shared\ndescription: Shared\n---\n\nBody.  \n",
    )

    with pytest.raises(ZppValidationError) as caught:
        merge_plugin_trait_indexes(
            (first_source, second_source),
            (first_index, second_index),
        )

    diagnostic = str(caught.value)
    assert "first@market" in diagnostic and str(first_source.plugin.root) in diagnostic
    assert "second@market" in diagnostic and str(second_source.plugin.root) in diagnostic


def test_schema_one_cache_is_recompiled_as_schema_two(tmp_path: Path) -> None:
    layer = LayerRef("global", tmp_path / ".zpp" / "global")
    authored = authored_layer_paths(layer.root)
    authored.traits.mkdir(parents=True)
    (authored.traits / "fresh.md").write_text(
        "---\nname: fresh\ndescription: Fresh\n---\n\nBody.\n",
        encoding="utf-8",
    )
    cache = trait_cache_paths(layer, user_root=tmp_path / ".zpp")
    cache.root.mkdir(parents=True)
    cache.index.write_text(
        json.dumps({"schema_version": 1, "traits": {}}),
        encoding="utf-8",
    )
    write_trait_cache_watchfile(cache.index, cache.watch)

    loaded = load_trait_index(authored, cache)

    assert loaded["schema_version"] == 2
    assert "fresh" in loaded["traits"]
