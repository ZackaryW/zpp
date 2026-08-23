import pytest

from zpp.core.catalog import decode_trait_document
from zpp.core.composition import CompositionError, compose_trait_family
from zpp.core.models import (
    ActivationMode,
    CompositionMode,
    SelectionPolicy,
    SourceKind,
    SourceRef,
)


def _document(
    source_kind: SourceKind,
    identifier: str,
    selection: str,
    body: str,
    *,
    mode: str | None = None,
    activation: str | None = None,
    order: int = 0,
):
    meta = {"selection": selection}
    if mode is not None:
        meta["mode"] = mode
    if activation is not None:
        meta["activation"] = activation
    return decode_trait_document(
        "bdd",
        {
            "meta": meta,
            "trait": [{"content": {"body": body}}],
        },
        SourceRef(kind=source_kind, identifier=identifier, order=order),
    )


def test_compose_trait_family_orders_sources_and_uses_repository_policy() -> None:
    effective = compose_trait_family(
        "bdd",
        [
            _document(SourceKind.GLOBAL, "global", "all", "global"),
            _document(SourceKind.REPOSITORY, "repository", "first-win", "repo"),
            _document(SourceKind.STORE, "store", "extend", "store"),
        ],
    )

    assert effective.selection is SelectionPolicy.FIRST_WIN
    assert effective.policy_source.identifier == "repository"
    assert [item.flavor.content.body for item in effective.flavors] == [
        "repo",
        "store",
        "global",
    ]


def test_compose_trait_family_preserves_order_inside_each_category() -> None:
    first = _document(SourceKind.STORE, "store-first", "all", "first", order=1)
    second = _document(SourceKind.STORE, "store-second", "extend", "second", order=2)

    effective = compose_trait_family("bdd", [second, first])

    assert [item.flavor.content.body for item in effective.flavors] == [
        "first",
        "second",
    ]


def test_selected_child_store_supplies_policy_when_repository_is_absent() -> None:
    parent = _document(SourceKind.STORE, "parent", "all", "parent", order=1)
    child = _document(SourceKind.STORE, "child", "first-win", "child", order=2)

    effective = compose_trait_family("bdd", [child, parent])

    assert effective.selection is SelectionPolicy.FIRST_WIN
    assert effective.policy_source.identifier == "child"
    assert [item.flavor.content.body for item in effective.flavors] == [
        "parent",
        "child",
    ]


def test_compose_trait_family_uses_highest_precedence_activation() -> None:
    effective = compose_trait_family(
        "bdd",
        [
            _document(
                SourceKind.GLOBAL,
                "global",
                "all",
                "global",
                activation="always-run",
            ),
            _document(
                SourceKind.REPOSITORY,
                "repository",
                "all",
                "repository",
                activation="manual",
            ),
        ],
    )

    assert effective.activation is ActivationMode.MANUAL


def test_repository_overwrite_excludes_store_and_global_contributions() -> None:
    effective = compose_trait_family(
        "bdd",
        [
            _document(SourceKind.GLOBAL, "global", "all", "global"),
            _document(SourceKind.STORE, "store", "all", "store"),
            _document(
                SourceKind.REPOSITORY,
                "repository",
                "extend",
                "repo",
                mode="repository-overwrite",
            ),
        ],
    )

    assert effective.mode is CompositionMode.REPOSITORY_OVERWRITE
    assert [item.flavor.content.body for item in effective.flavors] == ["repo"]
    assert [source.identifier for source in effective.excluded_sources] == [
        "store",
        "global",
    ]


def test_repository_overwrite_is_rejected_for_non_repository_source() -> None:
    with pytest.raises(CompositionError, match="only for repository"):
        compose_trait_family(
            "bdd",
            [
                _document(
                    SourceKind.STORE,
                    "store",
                    "extend",
                    "store",
                    mode="repository-overwrite",
                )
            ],
        )
