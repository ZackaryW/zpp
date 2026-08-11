from types import MappingProxyType

import pytest

from zpp.core.catalog import decode_trait_document
from zpp.core.composition import compose_trait_family
from zpp.core.models import EvidenceResult, ResolutionContext, SourceKind, SourceRef
from zpp.core.rendering import render_prompt_bodies
from zpp.core.resolution import (
    UnknownTraitFamilyError,
    evidence_ref,
    resolve_trait_family,
    resolve_traits,
)


def _family(
    selection: str,
    flavors: list[dict[str, object]],
    *,
    family: str = "bdd",
    activation: str | None = None,
):
    meta = {"selection": selection}
    if activation is not None:
        meta["activation"] = activation
    return compose_trait_family(
        family,
        [
            decode_trait_document(
                family,
                {"meta": meta, "trait": flavors},
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


def test_evidence_enriches_context_before_cross_family_selection() -> None:
    detector = _family(
        "first-win",
        [
            _flavor(
                "typescript evidence",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            )
        ],
        family="bdd",
    )
    consumer = _family(
        "first-win",
        [_flavor("typescript consumer", language="typescript")],
        family="build",
    )
    ref = evidence_ref(detector, detector.flavors[0], 0)

    result = resolve_traits(
        [detector, consumer],
        _context(),
        {ref: EvidenceResult(matched=True)},
    )

    assert result.context.values["language"] == "typescript"
    assert result.families[0].bodies == ("typescript evidence",)
    assert result.families[1].bodies == ("typescript consumer",)
    assert result.families[0].decisions[0].reason == "selected-evidence"
    assert result.families[0].decisions[0].evidence == ref


def test_first_win_direct_match_blocks_evidence_enrichment() -> None:
    family = _family(
        "first-win",
        [
            _flavor("python", language="python"),
            _flavor(
                "typescript evidence",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            ),
        ],
    )
    ref = evidence_ref(family, family.flavors[1], 0)

    result = resolve_traits(
        [family],
        _context(language="python"),
        {ref: EvidenceResult(matched=True)},
    )

    assert result.families[0].bodies == ("python",)
    assert result.context.values["language"] == "python"


@pytest.mark.parametrize("selection", ["all", "extend"])
def test_multi_match_policies_enrich_from_each_evidence_candidate(
    selection: str,
) -> None:
    family = _family(
        selection,
        [
            _flavor(
                "python",
                when=[{"workspace_contains": "/pyproject.toml"}],
                language="python",
            ),
            _flavor(
                "typescript",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            ),
        ],
    )
    evidence = {
        evidence_ref(family, flavor, 0): EvidenceResult(matched=True)
        for flavor in family.flavors
    }

    result = resolve_traits([family], _context(), evidence)

    assert result.context.values["language"] == ("python", "typescript")
    assert result.families[0].bodies == ("python", "typescript")


def test_repository_list_context_extends_with_unique_evidence_values() -> None:
    family = _family(
        "all",
        [
            _flavor(
                "python",
                when=[{"workspace_contains": "/pyproject.toml"}],
                language="python",
            ),
            _flavor(
                "typescript",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            ),
        ],
    )
    evidence = {
        evidence_ref(family, flavor, 0): EvidenceResult(matched=True)
        for flavor in family.flavors
    }
    context = ResolutionContext(
        values=MappingProxyType({"language": ("python", "rust")}),
        provenance=MappingProxyType({"language": "repository"}),
    )

    result = resolve_traits([family], context, evidence)

    assert result.context.values["language"] == (
        "python",
        "rust",
        "typescript",
    )
    assert [member.source for member in result.context.members["language"]] == [
        "repository",
        "repository",
        "evidence",
    ]


def test_invocation_list_context_is_not_extended_by_evidence() -> None:
    family = _family(
        "all",
        [
            _flavor(
                "typescript",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            )
        ],
    )
    ref = evidence_ref(family, family.flavors[0], 0)

    result = resolve_traits(
        [family],
        _context(language=("python", "rust")),
        {ref: EvidenceResult(matched=True)},
    )

    assert result.context.values["language"] == ("python", "rust")
    assert result.families[0].bodies == ()


def test_evidence_owned_scalar_extends_with_distinct_evidence_value() -> None:
    family = _family(
        "all",
        [
            _flavor(
                "typescript",
                when=[{"workspace_contains": "/cucumber.js"}],
                language="typescript",
            )
        ],
    )
    ref = evidence_ref(family, family.flavors[0], 0)
    context = ResolutionContext(
        values=MappingProxyType({"language": "python"}),
        provenance=MappingProxyType({"language": "evidence"}),
    )

    result = resolve_traits(
        [family],
        context,
        {ref: EvidenceResult(matched=True)},
    )

    assert result.context.values["language"] == ("python", "typescript")


def test_resolve_traits_publishes_false_evaluated_fact_with_fingerprint() -> None:
    family = _family(
        "first-win",
        [_flavor("uv", when=[{"which": "uv"}], build_tool="uv")],
    )
    ref = evidence_ref(family, family.flavors[0], 0)

    result = resolve_traits(
        [family],
        _context(),
        {
            ref: EvidenceResult(
                matched=False,
                facts=MappingProxyType({"has_uv": False}),
                fingerprints=MappingProxyType({"which:uv": "missing"}),
            )
        },
    )

    assert result.context.values["has_uv"] is False
    assert result.context.provenance["has_uv"] == "evidence"
    assert result.context.evidence["has_uv"] == ("which:uv",)
    assert result.context.fingerprints == {"which:uv": "missing"}


def test_resolve_traits_attaches_selected_backfill_fingerprint_provenance() -> None:
    family = _family(
        "extend",
        [
            _flavor("generic"),
            _flavor(
                "python",
                when=[{"workspace_contains": "/pyproject.toml"}],
                language="python",
            ),
        ],
    )
    selected = family.flavors[1]
    ref = evidence_ref(family, selected, 0)

    result = resolve_traits(
        [family],
        _context(),
        {
            ref: EvidenceResult(
                matched=True,
                fingerprints=MappingProxyType(
                    {"workspace_contains:/pyproject.toml": "present"}
                ),
            )
        },
    )

    assert result.families[0].bodies == ("python",)
    assert result.context.values["language"] == "python"
    assert result.context.evidence["language"] == (
        "workspace_contains:/pyproject.toml",
    )


def test_resolve_traits_does_not_replace_explicit_fact_with_evidence() -> None:
    family = _family(
        "first-win",
        [_flavor("uv", when=[{"which": "uv"}], build_tool="uv")],
    )
    ref = evidence_ref(family, family.flavors[0], 0)
    explicit = ResolutionContext(
        values=MappingProxyType({"has_uv": True}),
        provenance=MappingProxyType({"has_uv": "invocation"}),
    )

    result = resolve_traits(
        [family],
        explicit,
        {
            ref: EvidenceResult(
                matched=False,
                facts=MappingProxyType({"has_uv": False}),
                fingerprints=MappingProxyType({"which:uv": "missing"}),
            )
        },
    )

    assert result.context.values["has_uv"] is True
    assert result.context.provenance["has_uv"] == "invocation"
    assert "has_uv" not in result.context.evidence


def test_unfiltered_resolution_excludes_manual_families() -> None:
    automatic = _family("all", [_flavor("automatic")], family="automatic")
    manual = _family(
        "all",
        [_flavor("manual")],
        family="manual",
        activation="manual",
    )

    result = resolve_traits([automatic, manual], _context(), {})

    assert [family.family for family in result.families] == ["automatic"]


def test_requested_manual_family_uses_normal_activation_in_request_order() -> None:
    manual = _family(
        "all",
        [
            _flavor("python", language="python"),
            _flavor("flutter", language="flutter"),
        ],
        family="manual",
        activation="manual",
    )
    automatic = _family("all", [_flavor("automatic")], family="automatic")

    result = resolve_traits(
        [automatic, manual],
        _context(language="python"),
        {},
        requested=("manual", "automatic", "manual"),
    )

    assert [family.family for family in result.families] == [
        "manual",
        "automatic",
    ]
    assert result.families[0].bodies == ("python",)


def test_requested_unknown_family_is_rejected() -> None:
    family = _family("all", [_flavor("automatic")])

    with pytest.raises(UnknownTraitFamilyError, match="unknown"):
        resolve_traits([family], _context(), {}, requested=("unknown",))


def test_always_run_bypasses_activation_but_preserves_extend_without_backfill() -> None:
    family = _family(
        "extend",
        [
            _flavor("generic python", language="python"),
            _flavor("python uv", language="python", build_tool="uv"),
            _flavor("flutter", language="flutter"),
        ],
        activation="always-run",
    )

    result = resolve_traits([family], _context(), {})

    assert result.families[0].bodies == ("python uv", "flutter")
    assert result.context.values == {}


def test_render_prompt_bodies_preserves_complete_bodies_in_resolution_order() -> None:
    first = _family("all", [_flavor("first\nbody")], family="first")
    second = _family("all", [_flavor("second body")], family="second")
    result = resolve_traits([first, second], _context(), {})

    assert render_prompt_bodies(result) == "first\nbody\n\n---\n\nsecond body"


def test_render_prompt_bodies_returns_empty_string_without_selected_bodies() -> None:
    family = _family("all", [_flavor("python", language="python")])
    result = resolve_traits([family], _context(language="flutter"), {})

    assert render_prompt_bodies(result) == ""
