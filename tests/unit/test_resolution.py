from types import MappingProxyType

from zpp.catalog import decode_trait_document
from zpp.composition import compose_trait_family
from zpp.models import EvidenceResult, ResolutionContext, SourceKind, SourceRef
from zpp.resolution import evidence_ref, resolve_trait_family, resolve_traits


def _family(selection: str, flavors: list[dict[str, object]]):
    return compose_trait_family(
        "bdd",
        [
            decode_trait_document(
                "bdd",
                {"meta": {"selection": selection}, "trait": flavors},
                SourceRef(SourceKind.REPOSITORY, "repository"),
            )
        ],
    )


def _flavor(
    body: str,
    *,
    when: list[dict[str, object]] | None = None,
    **facets: str,
) -> dict[str, object]:
    result: dict[str, object] = {"facet": facets, "content": {"body": body}}
    if when is not None:
        result["when"] = when
    return result


def _context(**values: str | tuple[str, ...]) -> ResolutionContext:
    return ResolutionContext(
        values=MappingProxyType(values),
        provenance=MappingProxyType({key: "invocation" for key in values}),
    )


def test_extend_removes_dominated_match_and_retains_incomparable_match() -> None:
    family = _family(
        "extend",
        [
            _flavor("generic python", language="python"),
            _flavor("python uv", language="python", build_tool="uv"),
            _flavor("flutter", language="flutter"),
        ],
    )

    result = resolve_trait_family(
        family,
        _context(language=("python", "flutter"), build_tool="uv"),
        {},
    )

    assert result.bodies == ("python uv", "flutter")
    assert result.decisions[0].reason == "dominated"


def test_first_win_prefers_direct_match_before_evidence_fallback() -> None:
    family = _family(
        "first-win",
        [
            _flavor("python", language="python"),
            _flavor(
                "flutter",
                language="flutter",
                when=[{"workspace_contains": "/pubspec.yaml"}],
            ),
        ],
    )
    flutter = family.flavors[1]

    result = resolve_trait_family(
        family,
        _context(language="python"),
        {evidence_ref(family, flutter, 0): EvidenceResult(matched=True)},
    )

    assert result.bodies == ("python",)


def test_first_win_uses_first_compatible_successful_evidence_as_fallback() -> None:
    family = _family(
        "first-win",
        [
            _flavor(
                "flutter",
                language="flutter",
                when=[{"workspace_contains": "/pubspec.yaml"}],
            ),
            _flavor(
                "python",
                language="python",
                when=[{"workspace_contains": "/pyproject.toml"}],
            ),
        ],
    )
    evidence = {
        evidence_ref(family, flavor, 0): EvidenceResult(matched=True)
        for flavor in family.flavors
    }

    result = resolve_trait_family(family, _context(), evidence)

    assert result.bodies == ("flutter",)
    assert result.backfill.values == {"language": "flutter"}


def test_all_combines_direct_and_evidence_candidates_with_ordered_backfill() -> None:
    family = _family(
        "all",
        [
            _flavor("always"),
            _flavor(
                "python",
                language="python",
                when=[{"workspace_contains": "/pyproject.toml"}],
            ),
            _flavor(
                "flutter",
                language="flutter",
                when=[{"workspace_contains": "/pubspec.yaml"}],
            ),
        ],
    )
    evidence = {
        evidence_ref(family, flavor, 0): EvidenceResult(matched=True)
        for flavor in family.flavors[1:]
    }

    result = resolve_trait_family(family, _context(), evidence)

    assert result.bodies == ("always", "python", "flutter")
    assert result.backfill.values == {"language": ("python", "flutter")}


def test_extend_evidence_specialization_dominates_direct_generic_flavor() -> None:
    family = _family(
        "extend",
        [
            _flavor("generic"),
            _flavor(
                "python uv",
                language="python",
                build_tool="uv",
                when=[{"which": "uv"}],
            ),
        ],
    )
    specialized = family.flavors[1]

    result = resolve_trait_family(
        family,
        _context(),
        {evidence_ref(family, specialized, 0): EvidenceResult(matched=True)},
    )

    assert result.bodies == ("python uv",)
    assert result.backfill.values == {"language": "python", "build_tool": "uv"}


def test_extend_keeps_only_first_equal_facet_map() -> None:
    family = _family(
        "extend",
        [
            _flavor("first", language="python"),
            _flavor("second", language="python"),
        ],
    )

    result = resolve_trait_family(family, _context(language="python"), {})

    assert result.bodies == ("first",)


def test_unmatched_family_is_inactive_and_families_stack() -> None:
    inactive = _family("first-win", [_flavor("python", language="python")])
    active = compose_trait_family(
        "build",
        [
            decode_trait_document(
                "build",
                {
                    "meta": {"selection": "all"},
                    "trait": [_flavor("uv", build_tool="uv")],
                },
                SourceRef(SourceKind.GLOBAL, "global"),
            )
        ],
    )

    result = resolve_traits(
        [inactive, active],
        _context(language="flutter", build_tool="uv"),
        {},
    )

    assert result.families[0].bodies == ()
    assert result.families[1].bodies == ("uv",)
