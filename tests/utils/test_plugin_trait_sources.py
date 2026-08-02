import json
from pathlib import Path

import pytest

from zpp.utils.models import ManagedStateError, TriggerRule
from zpp.utils.plugin_discovery import ActivePlugin
from zpp.utils.plugin_trait_sources import (
    inspect_plugin_trait_source,
    load_plugin_trait_index,
    plugin_trait_cache_paths,
    read_plugin_trigger_rules,
)


def _plugin(root: Path, *, identity: str = "alpha@market", version: str = "1") -> ActivePlugin:
    root.mkdir(parents=True, exist_ok=True)
    return ActivePlugin("codex", identity, version, root.resolve())


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_plugin_trait_source_is_optional_but_partial_declarations_fail(
    tmp_path: Path,
) -> None:
    plugin = _plugin(tmp_path / "plugin")

    assert inspect_plugin_trait_source(plugin) is None

    (plugin.root / "trait.json").write_text("[]\n", encoding="utf-8")
    with pytest.raises(ManagedStateError, match="traits"):
        inspect_plugin_trait_source(plugin)


def test_plugin_trait_source_loads_controls_and_cache_without_source_writes(
    tmp_path: Path,
) -> None:
    plugin = _plugin(tmp_path / "plugin")
    traits = plugin.root / "traits"
    traits.mkdir()
    (plugin.root / "trait.json").write_text(
        json.dumps([{"trait": "manual"}], ensure_ascii=False),
        encoding="utf-8",
    )
    (traits / "manual.md").write_bytes(
        "---\nname: manual\ndescription: UTF-8 指引\n---\n\n  Keep spacing.  \n".encode(
            "utf-8"
        )
    )
    source = inspect_plugin_trait_source(plugin)
    assert source is not None
    before = _snapshot(plugin.root)
    user_root = tmp_path / "home" / ".zpp"

    rules = read_plugin_trigger_rules(source)
    index = load_plugin_trait_index(source, user_root=user_root)
    cache = plugin_trait_cache_paths(user_root, source)

    assert rules == (TriggerRule("manual"),)
    assert index["traits"]["manual"]["body"] == "\n  Keep spacing.  \n"
    assert cache.root.is_relative_to(user_root / "cached" / "plugins" / "codex")
    assert cache.index.is_file() and cache.watch.is_file()
    assert _snapshot(plugin.root) == before
    assert not (plugin.root / "cached").exists()


def test_plugin_cache_key_changes_with_identity_version_or_root(tmp_path: Path) -> None:
    user_root = tmp_path / "home" / ".zpp"
    first = _plugin(tmp_path / "one")
    second = _plugin(tmp_path / "two")
    for plugin in (first, second):
        (plugin.root / "traits").mkdir()
        (plugin.root / "trait.json").write_text("[]\n", encoding="utf-8")
    first_source = inspect_plugin_trait_source(first)
    second_source = inspect_plugin_trait_source(second)
    assert first_source is not None and second_source is not None

    same = plugin_trait_cache_paths(user_root, first_source)
    changed_root = plugin_trait_cache_paths(user_root, second_source)
    changed_version_source = inspect_plugin_trait_source(
        ActivePlugin("codex", first.identity, "2", first.root)
    )
    assert changed_version_source is not None
    changed_version = plugin_trait_cache_paths(user_root, changed_version_source)

    assert same == plugin_trait_cache_paths(user_root, first_source)
    assert len({same.root, changed_root.root, changed_version.root}) == 3


def test_malformed_plugin_trigger_document_is_source_oriented(tmp_path: Path) -> None:
    plugin = _plugin(tmp_path / "plugin")
    (plugin.root / "traits").mkdir()
    (plugin.root / "trait.json").write_text('{"not": "a list"}', encoding="utf-8")
    source = inspect_plugin_trait_source(plugin)
    assert source is not None

    with pytest.raises(ManagedStateError, match=r"trait\.json"):
        read_plugin_trigger_rules(source)
