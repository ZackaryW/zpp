from pathlib import Path, PurePosixPath

import pytest

from zpp.utils.authored_layers import (
    authored_layer_creation_plan,
    collect_authored_layer,
)
from zpp.utils.models import ZppValidationError
from zpp.utils.state_mutation import apply_creation_plan


def _write_valid_layer(root: Path) -> dict[PurePosixPath, bytes]:
    root.mkdir()
    traits = root / "traits"
    traits.mkdir()
    expected = {
        PurePosixPath("config.json"): (
            b'{ "traitsConfig": {}, "trait_overwrites": false }\n'
        ),
        PurePosixPath("trait.json"): b'[{"trait":"alpha"}]\n',
        PurePosixPath("traits/alpha.md"): (
            b"---\nname: alpha\ndescription: Alpha\n---\n\n  Keep spacing.  \n"
        ),
        PurePosixPath("traits/beta.md"): (
            "---\nname: beta\ndescription: 第二\n---\nBeta\n".encode()
        ),
    }
    for relative, content in expected.items():
        destination = root.joinpath(*relative.parts)
        destination.write_bytes(content)
    (root / "cached").mkdir()
    (root / "cached" / "traits.json").write_text("{}\n", encoding="utf-8")
    (root / "notes.txt").write_text("unmanaged", encoding="utf-8")
    return expected


def test_collect_and_recreate_only_valid_authored_layer_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    expected = _write_valid_layer(source)

    snapshot = collect_authored_layer(source)

    assert {item.relative_path: item.content for item in snapshot.files} == expected
    assert tuple(item.relative_path for item in snapshot.files) == tuple(expected)

    destination = tmp_path / "destination"
    apply_creation_plan(authored_layer_creation_plan(snapshot, destination))

    assert {
        path.relative_to(destination).as_posix(): path.read_bytes()
        for path in sorted(destination.rglob("*"))
        if path.is_file()
    } == {path.as_posix(): content for path, content in expected.items()}
    assert not (destination / "cached").exists()
    assert not (destination / "notes.txt").exists()


def test_collect_authored_layer_aggregates_source_errors_without_mutation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    _write_valid_layer(source)
    (source / "config.json").write_text("{", encoding="utf-8")
    (source / "trait.json").write_text('{"trait":"not-a-list"}', encoding="utf-8")
    (source / "traits" / "alpha.md").write_text(
        "---\nname: alpha\n---\nBody\n",
        encoding="utf-8",
    )
    (source / "traits" / "beta.md").write_text(
        "---\nname: wrong\ndescription: Wrong\n---\nBody\n",
        encoding="utf-8",
    )
    original = {path: path.read_bytes() for path in source.rglob("*") if path.is_file()}

    with pytest.raises(ZppValidationError) as caught:
        collect_authored_layer(source)

    assert len(caught.value.issues) >= 4
    assert {issue.source for issue in caught.value.issues} >= {
        source / "config.json",
        source / "trait.json",
        source / "traits" / "alpha.md",
        source / "traits" / "beta.md",
    }
    assert {path: path.read_bytes() for path in original} == original


def test_collect_authored_layer_rejects_trait_symlinks(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _write_valid_layer(source)
    linked_trait = source / "traits" / "linked.md"
    try:
        linked_trait.symlink_to(source / "traits" / "alpha.md")
    except OSError:
        pytest.skip("creating symlinks is unavailable on this system")

    with pytest.raises(ValueError, match="not a regular file"):
        collect_authored_layer(source)
