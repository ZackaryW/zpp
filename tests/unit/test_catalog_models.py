import pytest

from zpp.core.catalog import (
    TraitValidationError,
    decode_repository_context,
    decode_trait_document,
)
from zpp.core.models import ActivationMode, SelectionPolicy, SourceKind, SourceRef


def test_decode_trait_document_returns_ordered_immutable_flavors() -> None:
    source = SourceRef(kind=SourceKind.REPOSITORY, identifier="repository")

    document = decode_trait_document(
        "bdd",
        {
            "meta": {"selection": "extend"},
            "trait": [
                {
                    "facet": {"language": "python"},
                    "content": {"body": "Python guidance."},
                },
                {
                    "facet": {"language": "flutter"},
                    "content": {"body": "Flutter guidance."},
                },
            ],
        },
        source,
    )

    assert document.family == "bdd"
    assert document.selection is SelectionPolicy.EXTEND
    assert document.activation is ActivationMode.AUTOMATIC
    assert [flavor.content.body for flavor in document.flavors] == [
        "Python guidance.",
        "Flutter guidance.",
    ]
    assert document.source == source


def test_decode_trait_document_accepts_explicit_activation() -> None:
    document = decode_trait_document(
        "bdd",
        {
            "meta": {"selection": "all", "activation": "manual"},
            "trait": [{"content": {"body": "Manual guidance."}}],
        },
        SourceRef(kind=SourceKind.GLOBAL, identifier="global"),
    )

    assert document.activation is ActivationMode.MANUAL


def test_decode_trait_document_rejects_unsupported_activation() -> None:
    with pytest.raises(TraitValidationError) as caught:
        decode_trait_document(
            "bdd",
            {
                "meta": {"selection": "all", "activation": "sometimes"},
                "trait": [{"content": {"body": "Invalid."}}],
            },
            SourceRef(kind=SourceKind.GLOBAL, identifier="global"),
        )

    assert caught.value.location == ("meta", "activation")


def test_decode_repository_context_accepts_scalar_and_distinct_string_lists() -> None:
    context = decode_repository_context(
        {
            "facet": {
                "language": ["python", "flutter"],
                "build_tool": "uv",
            }
        },
        SourceRef(kind=SourceKind.REPOSITORY, identifier="repository"),
    )

    assert context.values == {
        "language": ("python", "flutter"),
        "build_tool": "uv",
    }


def test_decode_trait_document_reports_atomic_flavor_location() -> None:
    source = SourceRef(kind=SourceKind.GLOBAL, identifier="packaged")

    with pytest.raises(TraitValidationError) as caught:
        decode_trait_document(
            "bdd",
            {
                "meta": {"selection": "first-win"},
                "trait": [{"facet": {"language": "python"}}],
            },
            source,
        )

    assert caught.value.source == source
    assert caught.value.location == ("trait", 0, "content")


def test_first_win_rejects_an_obviously_unreachable_later_flavor() -> None:
    source = SourceRef(kind=SourceKind.GLOBAL, identifier="packaged")

    with pytest.raises(TraitValidationError, match="unreachable") as caught:
        decode_trait_document(
            "bdd",
            {
                "meta": {"selection": "first-win"},
                "trait": [
                    {
                        "facet": {"language": "python"},
                        "content": {"body": "generic"},
                    },
                    {
                        "facet": {
                            "language": "python",
                            "build_tool": "uv",
                        },
                        "content": {"body": "specific"},
                    },
                ],
            },
            source,
        )

    assert caught.value.location == ("trait", 1)


@pytest.mark.parametrize(
    "facet",
    [
        {"has_uv": True},
        {"language": []},
        {"language": ["python", "python"]},
        {"language": ["python", 3]},
    ],
)
def test_decode_repository_context_rejects_invalid_categorical_values(
    facet: dict[str, object],
) -> None:
    with pytest.raises(TraitValidationError):
        decode_repository_context(
            {"facet": facet},
            SourceRef(kind=SourceKind.REPOSITORY, identifier="repository"),
        )
