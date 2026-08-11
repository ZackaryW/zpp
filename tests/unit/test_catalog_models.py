import pytest

from zpp.catalog import (
    TraitValidationError,
    decode_repository_context,
    decode_trait_document,
)
from zpp.models import SelectionPolicy, SourceKind, SourceRef


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
    assert [flavor.content.body for flavor in document.flavors] == [
        "Python guidance.",
        "Flutter guidance.",
    ]
    assert document.source == source


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
