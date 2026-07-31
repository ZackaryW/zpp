from pathlib import Path

import pytest

import zpp.utils.layer_transactions as layer_transactions
from zpp.utils.authored_layers import collect_authored_layer
from zpp.utils.layer_transactions import archive_and_replace_authored_layer
from zpp.utils.layouts import authored_layer_paths
from zpp.utils.models import CreationPlan


def _write_layer(root: Path, trait: str, body: str) -> None:
    root.mkdir(parents=True)
    (root / "traits").mkdir()
    (root / "config.json").write_text(
        '{ "traitsConfig": {}, "trait_overwrites": false }\n',
        encoding="utf-8",
    )
    (root / "trait.json").write_text(
        f'[{{"trait":"{trait}"}}]\n',
        encoding="utf-8",
    )
    (root / "traits" / f"{trait}.md").write_text(
        f"---\nname: {trait}\ndescription: {trait}\n---\n{body}\n",
        encoding="utf-8",
    )


def _authored_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_archive_and_replace_authored_layer_preserves_sources_and_invalidates_cache(
    tmp_path: Path,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    cache = tmp_path / "cached" / "global"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    (cache / "traits.watch.json").write_text("{}\n", encoding="utf-8")
    old_bytes = _authored_bytes(current)
    replacement_bytes = _authored_bytes(replacement_source)
    replacement = collect_authored_layer(replacement_source)

    archive_and_replace_authored_layer(
        authored_layer_paths(current),
        replacement,
        archive,
        (cache,),
    )

    assert _authored_bytes(archive) == old_bytes
    assert _authored_bytes(current) == replacement_bytes
    assert _authored_bytes(replacement_source) == replacement_bytes
    assert not cache.exists()
    assert not tuple(tmp_path.rglob("*.zpp-remove-*"))


def test_archive_and_replace_authored_layer_rolls_back_a_late_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    cache = tmp_path / "cached" / "global"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text('{"old": true}\n', encoding="utf-8")
    old_bytes = _authored_bytes(current)
    cache_bytes = _authored_bytes(cache)
    replacement = collect_authored_layer(replacement_source)
    apply_creation_plan = layer_transactions.apply_creation_plan

    def fail_after_install(plan: CreationPlan) -> None:
        apply_creation_plan(plan)
        raise RuntimeError("late installation failure")

    monkeypatch.setattr(
        layer_transactions,
        "apply_creation_plan",
        fail_after_install,
    )

    with pytest.raises(RuntimeError, match="late installation failure"):
        archive_and_replace_authored_layer(
            authored_layer_paths(current),
            replacement,
            archive,
            (cache,),
        )

    assert _authored_bytes(current) == old_bytes
    assert _authored_bytes(cache) == cache_bytes
    assert not archive.exists()


def test_archive_and_replace_authored_layer_rejects_an_existing_archive(
    tmp_path: Path,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    cache = tmp_path / "cached" / "global"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    archive.mkdir()
    (archive / "marker").write_text("occupied", encoding="utf-8")
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    old_bytes = _authored_bytes(current)
    cache_bytes = _authored_bytes(cache)

    with pytest.raises(FileExistsError):
        archive_and_replace_authored_layer(
            authored_layer_paths(current),
            collect_authored_layer(replacement_source),
            archive,
            (cache,),
        )

    assert _authored_bytes(current) == old_bytes
    assert _authored_bytes(cache) == cache_bytes
    assert (archive / "marker").read_text(encoding="utf-8") == "occupied"


def test_archive_and_replace_authored_layer_rejects_an_invalid_current_layer(
    tmp_path: Path,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    cache = tmp_path / "cached" / "global"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    (current / "trait.json").unlink()
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    old_bytes = _authored_bytes(current)
    cache_bytes = _authored_bytes(cache)

    with pytest.raises(ValueError, match="not a regular file"):
        archive_and_replace_authored_layer(
            authored_layer_paths(current),
            collect_authored_layer(replacement_source),
            archive,
            (cache,),
        )

    assert _authored_bytes(current) == old_bytes
    assert _authored_bytes(cache) == cache_bytes
    assert not archive.exists()


def test_archive_and_replace_authored_layer_restores_cache_after_archive_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    cache = tmp_path / "cached" / "global"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    old_bytes = _authored_bytes(current)
    cache_bytes = _authored_bytes(cache)
    replace = Path.replace

    def fail_archive(source: Path, target: Path) -> Path:
        if source == current and target == archive:
            raise OSError("archive failure")
        return replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_archive)

    with pytest.raises(OSError, match="archive failure"):
        archive_and_replace_authored_layer(
            authored_layer_paths(current),
            collect_authored_layer(replacement_source),
            archive,
            (cache,),
        )

    assert _authored_bytes(current) == old_bytes
    assert _authored_bytes(cache) == cache_bytes
    assert not archive.exists()


def test_archive_and_replace_authored_layer_leaves_state_after_cache_staging_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = tmp_path / "global"
    replacement_source = tmp_path / "profiles" / "default"
    archive = tmp_path / "profiles" / "20260730-143522-global"
    first_cache = tmp_path / "cached" / "global"
    second_cache = tmp_path / "cached" / "profiles" / "default"
    _write_layer(current, "old", "old body")
    _write_layer(replacement_source, "new", "new body")
    first_cache.mkdir(parents=True)
    second_cache.mkdir(parents=True)
    (first_cache / "traits.json").write_text('{"first": true}\n', encoding="utf-8")
    (second_cache / "traits.json").write_text(
        '{"second": true}\n',
        encoding="utf-8",
    )
    old_bytes = _authored_bytes(current)
    first_cache_bytes = _authored_bytes(first_cache)
    second_cache_bytes = _authored_bytes(second_cache)
    replace = Path.replace

    def fail_second_cache(source: Path, target: Path) -> Path:
        if source == second_cache:
            raise OSError("cache staging failure")
        return replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_second_cache)

    with pytest.raises(OSError, match="cache staging failure"):
        archive_and_replace_authored_layer(
            authored_layer_paths(current),
            collect_authored_layer(replacement_source),
            archive,
            (first_cache, second_cache),
        )

    assert _authored_bytes(current) == old_bytes
    assert _authored_bytes(first_cache) == first_cache_bytes
    assert _authored_bytes(second_cache) == second_cache_bytes
    assert not archive.exists()
