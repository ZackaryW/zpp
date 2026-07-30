from pathlib import Path

from zpp.utils.models import SavedBinding, SavedIndex
from zpp.utils.paths import (
    bind_saved_target,
    canonicalize_existing_directory,
    closest_saved_binding,
    ordered_saved_bindings,
    path_is_within,
    unbind_saved_name,
    validate_layer_name,
)


def test_canonical_directories_select_the_closest_real_ancestor(tmp_path: Path) -> None:
    outer = tmp_path / "work"
    inner = outer / "project"
    target_path = inner / "src"
    target_path.mkdir(parents=True)
    misleading = tmp_path / "work-other"
    misleading.mkdir()

    target = canonicalize_existing_directory(target_path / ".." / "src")
    outer_directory = canonicalize_existing_directory(outer)
    inner_directory = canonicalize_existing_directory(inner)
    misleading_directory = canonicalize_existing_directory(misleading)
    bindings = (
        SavedBinding(name="outer", target=outer_directory),
        SavedBinding(name="inner", target=inner_directory),
        SavedBinding(name="misleading", target=misleading_directory),
    )

    assert path_is_within(target, outer_directory) is True
    assert path_is_within(target, misleading_directory) is False
    assert closest_saved_binding(target, bindings) == bindings[1]


def test_saved_index_operations_are_immutable_idempotent_and_ordered(
    tmp_path: Path,
) -> None:
    alpha = tmp_path / "alpha"
    zeta = tmp_path / "zeta"
    alpha.mkdir()
    zeta.mkdir()
    original = SavedIndex({str(zeta.resolve()): "shared"})

    bound = bind_saved_target(
        original,
        name=validate_layer_name("shared_1"),
        target=canonicalize_existing_directory(alpha),
    )
    rebound = bind_saved_target(
        bound,
        name="shared_1",
        target=canonicalize_existing_directory(alpha),
    )

    assert original.bindings == {str(zeta.resolve()): "shared"}
    assert rebound == bound
    assert [(item.name, item.target.resolved) for item in ordered_saved_bindings(bound)] == [
        ("shared_1", alpha.resolve()),
        ("shared", zeta.resolve()),
    ]
    assert unbind_saved_name(bound, name="shared_1") == original
