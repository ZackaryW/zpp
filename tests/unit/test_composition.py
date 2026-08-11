import pytest

from zpp.catalog import decode_trait_document
from zpp.composition import CompositionError, compose_trait_family
from zpp.models import CompositionMode, SelectionPolicy, SourceKind, SourceRef


def _document(
    source_kind: SourceKind,
    identifier: str,
    selection: str,
    body: str,
    *,
    mode: str | None = None,
    order: int = 0,
):
    meta = {"selection": selection}
    if mode is not None:
        meta["mode"] = mode
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
            _document(SourceKind.SPACE, "space", "extend", "space"),
        ],
    )

    assert effective.selection is SelectionPolicy.FIRST_WIN
    assert effective.policy_source.identifier == "repository"
    assert [item.flavor.content.body for item in effective.flavors] == [
        "repo",
        "space",
        "global",
    ]


def test_compose_trait_family_preserves_order_inside_each_category() -> None:
    first = _document(SourceKind.SPACE, "space-first", "all", "first", order=1)
    second = _document(SourceKind.SPACE, "space-second", "extend", "second", order=2)

    effective = compose_trait_family("bdd", [second, first])

    assert [item.flavor.content.body for item in effective.flavors] == [
        "first",
        "second",
    ]


def test_repository_overwrite_excludes_space_and_global_contributions() -> None:
    effective = compose_trait_family(
        "bdd",
        [
            _document(SourceKind.GLOBAL, "global", "all", "global"),
            _document(SourceKind.SPACE, "space", "all", "space"),
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
        "space",
        "global",
    ]


def test_repository_overwrite_is_rejected_for_non_repository_source() -> None:
    with pytest.raises(CompositionError, match="only for repository"):
        compose_trait_family(
            "bdd",
            [
                _document(
                    SourceKind.SPACE,
                    "space",
                    "extend",
                    "space",
                    mode="repository-overwrite",
                )
            ],
        )
